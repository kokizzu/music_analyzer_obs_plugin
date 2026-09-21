#pragma once

// Native shared-mode speaker capture: no virtual cable or external process.
#ifdef _WIN32
#include <audioclient.h>
#include <mmdeviceapi.h>
#include <functiondiscoverykeys_devpkey.h>
#include <ks.h>
#include <ksmedia.h>
#include <chrono>
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>

class WindowsLoopback {
	static constexpr uint32_t kEndpointQueryGraceChecks = 4;
	static constexpr uint32_t kCaptureErrorGraceChecks = 3;
	IMMDeviceEnumerator *enumerator_ = nullptr;
	IMMDevice *device_ = nullptr;
	IAudioClient *client_ = nullptr;
	IAudioCaptureClient *capture_ = nullptr;
	WAVEFORMATEX *format_ = nullptr;
	bool com_ = false;
	bool input_ = false;
	HANDLE ready_ = nullptr;
	bool floating_ = false;
	UINT32 channel_stride_ = 0;
	ERole endpoint_role_ = eMultimedia;
	std::wstring device_id_;
	std::chrono::steady_clock::time_point next_endpoint_check_{};
	uint32_t endpoint_query_failures_ = 0;
	uint32_t capture_error_failures_ = 0;
	std::vector<float> samples_;
	std::vector<double> channel_squares_;
	std::vector<float> channel_peaks_;
	bool diagnostics_ = false;
	uint64_t diagnostic_packets_ = 0;
	uint64_t diagnostic_frames_ = 0;
	uint64_t diagnostic_silent_frames_ = 0;
	double diagnostic_square_sum_ = 0.0;
	float diagnostic_peak_ = 0.0f;
	std::chrono::steady_clock::time_point next_diagnostics_log_{};

	void reset_diagnostics()
	{
		diagnostic_packets_ = 0;
		diagnostic_frames_ = 0;
		diagnostic_silent_frames_ = 0;
		diagnostic_square_sum_ = 0.0;
		diagnostic_peak_ = 0.0f;
	}

	bool check(HRESULT result, const char *step)
	{
		if (SUCCEEDED(result)) return true;
		std::fprintf(stderr, "WASAPI %s failed: HRESULT 0x%08lx\n", step, static_cast<unsigned long>(result));
		close();
		return false;
	}

	bool endpoint_query_failed(const char *step, HRESULT result)
	{
		++endpoint_query_failures_;
		std::fprintf(stderr, "WASAPI endpoint query error: step=%s HRESULT=0x%08lx attempt=%u\n",
			step, static_cast<unsigned long>(result), endpoint_query_failures_);
		if (endpoint_query_failures_ < kEndpointQueryGraceChecks)
			return false;
		std::fprintf(stderr, "WASAPI %s failed repeatedly: HRESULT 0x%08lx; reopening loopback\n", step,
			     static_cast<unsigned long>(result));
		close();
		return true;
	}

	bool capture_result(HRESULT result, const char *step)
	{
		if (SUCCEEDED(result)) {
			capture_error_failures_ = 0;
			return true;
		}
		std::fprintf(stderr, "WASAPI capture error: step=%s HRESULT=0x%08lx prior_failures=%u\n",
			step, static_cast<unsigned long>(result), capture_error_failures_);
		if (result == AUDCLNT_E_BUFFER_ERROR && ++capture_error_failures_ < kCaptureErrorGraceChecks)
			return true;
		capture_error_failures_ = 0;
		return check(result, step);
	}
public:
	~WindowsLoopback() { close(); }
	void close()
	{
		if (client_) client_->Stop();
		if (capture_) capture_->Release();
		if (client_) client_->Release();
		if (ready_) CloseHandle(ready_);
		ready_ = nullptr;
		if (device_) device_->Release();
		if (enumerator_) enumerator_->Release();
		if (format_) CoTaskMemFree(format_);
		capture_ = nullptr; client_ = nullptr; device_ = nullptr; enumerator_ = nullptr; format_ = nullptr;
		channel_stride_ = 0;
		endpoint_role_ = eMultimedia;
		device_id_.clear();
		next_endpoint_check_ = {};
		endpoint_query_failures_ = 0;
		capture_error_failures_ = 0;
		reset_diagnostics();
		if (com_) CoUninitialize();
		com_ = false;
	}
	void set_diagnostics(bool enabled)
	{
		diagnostics_ = enabled;
		reset_diagnostics();
		next_diagnostics_log_ = std::chrono::steady_clock::now() + std::chrono::seconds(1);
		std::fprintf(stderr, "WASAPI diagnostics: %s\n", enabled ? "enabled" : "disabled");
	}
	void maybe_log_diagnostics()
	{
		if (!diagnostics_)
			return;
		const auto now = std::chrono::steady_clock::now();
		if (now < next_diagnostics_log_)
			return;
		const double rms = diagnostic_frames_ == 0
			? 0.0
			: std::sqrt(diagnostic_square_sum_ / static_cast<double>(diagnostic_frames_));
		std::fprintf(stderr,
			     "WASAPI audio diagnostics: endpoint=%ls packets=%llu frames=%llu silent_frames=%llu rms=%.4f peak=%.4f\n",
			     device_id_.empty() ? L"(none)" : device_id_.c_str(),
			     static_cast<unsigned long long>(diagnostic_packets_),
			     static_cast<unsigned long long>(diagnostic_frames_),
			     static_cast<unsigned long long>(diagnostic_silent_frames_), rms, diagnostic_peak_);
		reset_diagnostics();
		next_diagnostics_log_ = now + std::chrono::seconds(1);
	}
	bool open(uint32_t &sample_rate, const char *input_name = nullptr)
	{
		close();
		input_ = input_name != nullptr;
		HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
		com_ = SUCCEEDED(hr);
		if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) return check(hr, "COM initialization");
		if (!check(CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL,
			__uuidof(IMMDeviceEnumerator), reinterpret_cast<void **>(&enumerator_)), "enumerator")) return false;
		endpoint_role_ = eMultimedia;
		HRESULT endpoint_result = E_NOTFOUND;
		if (input_ && input_name[0]) {
			IMMDeviceCollection *devices = nullptr;
			if (!check(enumerator_->EnumAudioEndpoints(eCapture, DEVICE_STATE_ACTIVE, &devices), "enumerate inputs")) return false;
			UINT count = 0;
			HRESULT count_result = devices->GetCount(&count);
			if (FAILED(count_result)) { devices->Release(); return check(count_result, "input count"); }
			for (UINT i = 0; i < count; ++i) {
				IMMDevice *candidate = nullptr;
				IPropertyStore *properties = nullptr;
				PROPVARIANT name;
				PropVariantInit(&name);
				HRESULT result = devices->Item(i, &candidate);
				if (SUCCEEDED(result)) result = candidate->OpenPropertyStore(STGM_READ, &properties);
				// PKEY_Device_FriendlyName, defined locally for MinGW SDKs whose
				// uuid library omits this property-key symbol.
				static constexpr PROPERTYKEY friendly_name = {
					{0xa45c254e, 0xdf1c, 0x4efd, {0x80, 0x20, 0x67, 0xd1, 0x46, 0xa8, 0x50, 0xe0}}, 14};
				if (SUCCEEDED(result)) result = properties->GetValue(friendly_name, &name);
				bool match = false;
				if (SUCCEEDED(result) && name.vt == VT_LPWSTR && name.pwszVal) {
					const int bytes = WideCharToMultiByte(CP_UTF8, 0, name.pwszVal, -1, nullptr, 0, nullptr, nullptr);
					std::string utf8(bytes > 0 ? bytes : 1, '\0');
					if (bytes > 0) WideCharToMultiByte(CP_UTF8, 0, name.pwszVal, -1, utf8.data(), bytes, nullptr, nullptr);
					std::fprintf(stderr, "WASAPI input candidate: %s\n", utf8.c_str());
					match = std::strcmp(utf8.c_str(), input_name) == 0;
				} else if (FAILED(result)) {
					std::fprintf(stderr, "WASAPI input enumeration error: HRESULT=0x%08lx\n", static_cast<unsigned long>(result));
				}
				PropVariantClear(&name);
				if (properties) properties->Release();
				if (match) { device_ = candidate; endpoint_result = S_OK; break; }
				if (candidate) candidate->Release();
			}
			devices->Release();
		} else {
			endpoint_result = enumerator_->GetDefaultAudioEndpoint(input_ ? eCapture : eRender, endpoint_role_, &device_);
		}
		if (FAILED(endpoint_result)) {
			if (input_ && input_name[0]) return check(endpoint_result, "named capture endpoint");
			endpoint_role_ = eConsole;
			endpoint_result = enumerator_->GetDefaultAudioEndpoint(input_ ? eCapture : eRender, endpoint_role_, &device_);
		}
		if (!check(endpoint_result, "default speakers")) return false;
		LPWSTR device_id = nullptr;
		if (!check(device_->GetId(&device_id), "speaker identity")) return false;
		if (!device_id) return check(E_UNEXPECTED, "speaker identity");
		device_id_ = device_id;
		CoTaskMemFree(device_id);
		if (!check(device_->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr,
			reinterpret_cast<void **>(&client_)), "audio client")) return false;
		if (input_) {
			IAudioClient2 *client2 = nullptr;
			HRESULT result = client_->QueryInterface(__uuidof(IAudioClient2), reinterpret_cast<void **>(&client2));
			if (SUCCEEDED(result)) {
				AudioClientProperties properties = {};
				properties.cbSize = sizeof(properties);
				properties.eCategory = AudioCategory_Media;
				properties.Options = AUDCLNT_STREAMOPTIONS_RAW;
				result = client2->SetClientProperties(&properties);
				std::fprintf(stderr, "WASAPI raw input request: HRESULT=0x%08lx accepted=%d\n", static_cast<unsigned long>(result), SUCCEEDED(result));
				if (FAILED(result)) {
					properties.Options = AUDCLNT_STREAMOPTIONS_NONE;
					result = client2->SetClientProperties(&properties);
					std::fprintf(stderr, "WASAPI processed-input fallback: HRESULT=0x%08lx\n", static_cast<unsigned long>(result));
				}
				client2->Release();
			} else std::fprintf(stderr, "WASAPI IAudioClient2 unavailable: HRESULT=0x%08lx; using default processing\n", static_cast<unsigned long>(result));
		}
		if (!check(client_->GetMixFormat(&format_), "mix format")) return false;
		WORD tag = format_->wFormatTag;
		if (tag == WAVE_FORMAT_EXTENSIBLE && format_->cbSize >= 22) {
			auto ext = reinterpret_cast<WAVEFORMATEXTENSIBLE *>(format_);
			if (IsEqualGUID(ext->SubFormat, KSDATAFORMAT_SUBTYPE_IEEE_FLOAT)) tag = WAVE_FORMAT_IEEE_FLOAT;
			else if (IsEqualGUID(ext->SubFormat, KSDATAFORMAT_SUBTYPE_PCM)) tag = WAVE_FORMAT_PCM;
		}
		floating_ = tag == WAVE_FORMAT_IEEE_FLOAT && format_->wBitsPerSample == 32;
		if ((!floating_ && !(tag == WAVE_FORMAT_PCM &&
						 (format_->wBitsPerSample == 16 || format_->wBitsPerSample == 24 ||
						  format_->wBitsPerSample == 32))) ||
			!format_->nChannels || !format_->nBlockAlign ||
			format_->nBlockAlign % format_->nChannels != 0)
			return check(AUDCLNT_E_UNSUPPORTED_FORMAT, "expected float32/PCM16/PCM24/PCM32");
		channel_stride_ = format_->nBlockAlign / format_->nChannels;
		const UINT32 minimum_sample_bytes = format_->wBitsPerSample / 8;
		if (channel_stride_ < minimum_sample_bytes || (floating_ && channel_stride_ < sizeof(float)))
			return check(AUDCLNT_E_UNSUPPORTED_FORMAT, "invalid channel stride");
		// DSP runs on the UI thread, so leave enough shared-mode headroom for a
		// complete analysis pass without allowing the endpoint to overrun.
		constexpr REFERENCE_TIME kBufferDuration = 100 * 10000;
		if (!check(client_->Initialize(AUDCLNT_SHAREMODE_SHARED, input_ ? AUDCLNT_STREAMFLAGS_EVENTCALLBACK : AUDCLNT_STREAMFLAGS_LOOPBACK,
			kBufferDuration, 0, format_, nullptr), "initialize loopback")) return false;
		if (input_) {
			ready_ = CreateEventW(nullptr, FALSE, FALSE, nullptr);
			if (!ready_) return check(HRESULT_FROM_WIN32(GetLastError()), "create capture event");
			if (!check(client_->SetEventHandle(ready_), "capture event")) return false;
		}
		UINT32 capacity = 0;
		if (!check(client_->GetBufferSize(&capacity), "buffer size")) return false;
		samples_.resize(capacity);
		channel_squares_.resize(format_->nChannels);
		channel_peaks_.resize(format_->nChannels);
		if (!check(client_->GetService(__uuidof(IAudioCaptureClient), reinterpret_cast<void **>(&capture_)), "capture service")) return false;
		if (!check(client_->Start(), "start")) return false;
		sample_rate = format_->nSamplesPerSec;
		std::fprintf(stderr, "WASAPI opened: input=%d endpoint=%ls rate=%u channels=%u bits=%u stride=%u buffer_frames=%u\n",
			input_, device_id_.c_str(), sample_rate, format_->nChannels, format_->wBitsPerSample, channel_stride_, capacity);
		std::fprintf(stderr, "WASAPI %s: %lu Hz, %u channels\n", input_ ? "native input" : "speaker loopback", static_cast<unsigned long>(sample_rate), format_->nChannels);
		return true;
	}
	bool active() const { return capture_ != nullptr; }
	bool wait_input()
	{
		const DWORD result = WaitForSingleObject(ready_, 100);
		if (result == WAIT_OBJECT_0) return true;
		if (result == WAIT_TIMEOUT) {
			std::fprintf(stderr, "WASAPI input event timeout: t=%lu\n", static_cast<unsigned long>(GetTickCount()));
			return true;
		}
		return check(HRESULT_FROM_WIN32(GetLastError()), "wait input event");
	}
	bool endpoint_changed()
	{
		if (!active() || !enumerator_ || device_id_.empty())
			return false;
		const auto now = std::chrono::steady_clock::now();
		if (now < next_endpoint_check_)
			return false;
		next_endpoint_check_ = now + std::chrono::milliseconds(500);

		IMMDevice *current_device = nullptr;
		HRESULT result = input_
			? enumerator_->GetDevice(device_id_.c_str(), &current_device)
			: enumerator_->GetDefaultAudioEndpoint(eRender, endpoint_role_, &current_device);
		if (!input_ && FAILED(result) && endpoint_role_ != eConsole) {
			result = enumerator_->GetDefaultAudioEndpoint(eRender, eConsole, &current_device);
		}
		if (FAILED(result)) {
			if (current_device)
				current_device->Release();
			return endpoint_query_failed(input_ ? "capture endpoint query" : "default speaker query", result);
		}

		LPWSTR current_id = nullptr;
		result = current_device->GetId(&current_id);
		if (FAILED(result) || !current_id) {
			if (current_id)
				CoTaskMemFree(current_id);
			current_device->Release();
			const HRESULT failure = FAILED(result) ? result : E_UNEXPECTED;
			return endpoint_query_failed(input_ ? "capture identity query" : "speaker identity query", failure);
		}
		endpoint_query_failures_ = 0;
		const bool changed = device_id_ != current_id;
		if (current_id)
			CoTaskMemFree(current_id);
		current_device->Release();
		if (!changed)
			return false;
		std::fprintf(stderr, "WASAPI %s endpoint changed; reopening capture\n",
			     input_ ? "capture" : "default speaker");
		close();
		return true;
	}
	template<class Feed> bool pump(Feed feed)
	{
		if (!capture_) return false;
		// Bound the work per UI iteration, without retaining an unbounded queue.
		for (int packet = 0; packet < 32; ++packet) {
			UINT32 pending = 0;
			const HRESULT next_result = capture_->GetNextPacketSize(&pending);
			if (next_result == AUDCLNT_S_BUFFER_EMPTY)
				return true;
			if (!capture_result(next_result, "next packet")) return false;
			if (!pending) return true;
			BYTE *data = nullptr; UINT32 frames = 0; DWORD flags = 0;
			const HRESULT buffer_result = capture_->GetBuffer(&data, &frames, &flags, nullptr, nullptr);
			if (buffer_result == AUDCLNT_S_BUFFER_EMPTY)
				return true;
			if (!capture_result(buffer_result, "read packet")) return false;
			if (FAILED(buffer_result)) return true; // No buffer was acquired; retry on the next wake.
			if (frames > samples_.size()) {
				capture_->ReleaseBuffer(frames);
				return check(E_UNEXPECTED, "packet larger than endpoint buffer");
			}
			if (diagnostics_)
				++diagnostic_packets_;
			std::fill(channel_squares_.begin(), channel_squares_.end(), 0.0);
			std::fill(channel_peaks_.begin(), channel_peaks_.end(), 0.0f);
			for (UINT32 frame = 0; frame < frames; ++frame) {
				float mono = 0.0f;
				const bool silent = (flags & AUDCLNT_BUFFERFLAGS_SILENT) != 0;
				if (!silent) {
					for (WORD ch = 0; ch < format_->nChannels; ++ch) {
						const BYTE *p = data + frame * format_->nBlockAlign + ch * channel_stride_;
						float value = 0.0f;
						if (floating_) std::memcpy(&value, p, 4);
						else if (format_->wBitsPerSample == 16) { int16_t v; std::memcpy(&v,p,2); value = v / 32768.0f; }
						else if (format_->wBitsPerSample == 24) {
							int32_t v = static_cast<int32_t>(p[0]) |
								(static_cast<int32_t>(p[1]) << 8) |
								(static_cast<int32_t>(p[2]) << 16);
							if (v & 0x00800000)
								v |= static_cast<int32_t>(0xff000000);
							value = static_cast<float>(v / 8388608.0);
						}
						else { int32_t v; std::memcpy(&v,p,4); value = static_cast<float>(v / 2147483648.0); }
						if (!std::isfinite(value)) {
							std::fprintf(stderr, "WASAPI invalid sample: channel=%u frame=%u\n", ch, frame);
							value = 0;
						}
						channel_squares_[ch] += static_cast<double>(value) * value;
						channel_peaks_[ch] = std::max(channel_peaks_[ch], std::fabs(value));
						mono += value / format_->nChannels;
					}
				}
				samples_[frame] = std::isfinite(mono) ? mono : 0.0f;
				if (diagnostics_) {
					++diagnostic_frames_;
					if (silent)
						++diagnostic_silent_frames_;
					const float magnitude = std::fabs(samples_[frame]);
					diagnostic_square_sum_ += static_cast<double>(samples_[frame]) * samples_[frame];
					if (magnitude > diagnostic_peak_)
						diagnostic_peak_ = magnitude;
				}
			}
			if (!check(capture_->ReleaseBuffer(frames), "release packet")) return false;
			if (input_ && diagnostics_) {
				for (WORD ch = 0; ch < format_->nChannels; ++ch)
					std::fprintf(stderr, "WASAPI native packet: t=%lu frames=%u flags=0x%lx channel=%u rms=%.9f peak=%.9f\n",
						static_cast<unsigned long>(GetTickCount()), frames, static_cast<unsigned long>(flags), ch,
						frames ? std::sqrt(channel_squares_[ch] / frames) : 0.0, static_cast<double>(channel_peaks_[ch]));
			}
			// Release the OS capture buffer before potentially expensive DSP work.
			for (UINT32 frame = 0; frame < frames; ++frame) feed(samples_[frame]);
		}
		return true;
	}
};
#endif
