#pragma once

// Native shared-mode speaker capture: no virtual cable or external process.
#ifdef _WIN32
#include <audioclient.h>
#include <mmdeviceapi.h>
#include <ks.h>
#include <ksmedia.h>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <cstdint>
#include <string>
#include <vector>

class WindowsLoopback {
	IMMDeviceEnumerator *enumerator_ = nullptr;
	IMMDevice *device_ = nullptr;
	IAudioClient *client_ = nullptr;
	IAudioCaptureClient *capture_ = nullptr;
	WAVEFORMATEX *format_ = nullptr;
	bool com_ = false;
	bool floating_ = false;
	UINT32 channel_stride_ = 0;
	ERole endpoint_role_ = eMultimedia;
	std::wstring device_id_;
	std::chrono::steady_clock::time_point next_endpoint_check_{};
	std::vector<float> samples_;
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
public:
	~WindowsLoopback() { close(); }
	void close()
	{
		if (client_) client_->Stop();
		if (capture_) capture_->Release();
		if (client_) client_->Release();
		if (device_) device_->Release();
		if (enumerator_) enumerator_->Release();
		if (format_) CoTaskMemFree(format_);
		capture_ = nullptr; client_ = nullptr; device_ = nullptr; enumerator_ = nullptr; format_ = nullptr;
		channel_stride_ = 0;
		endpoint_role_ = eMultimedia;
		device_id_.clear();
		next_endpoint_check_ = {};
		reset_diagnostics();
		if (com_) CoUninitialize();
		com_ = false;
	}
	void set_diagnostics(bool enabled)
	{
		diagnostics_ = enabled;
		reset_diagnostics();
		next_diagnostics_log_ = std::chrono::steady_clock::now() + std::chrono::seconds(1);
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
	bool open(uint32_t &sample_rate)
	{
		close();
		HRESULT hr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
		com_ = SUCCEEDED(hr);
		if (FAILED(hr) && hr != RPC_E_CHANGED_MODE) return check(hr, "COM initialization");
		if (!check(CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr, CLSCTX_ALL,
			__uuidof(IMMDeviceEnumerator), reinterpret_cast<void **>(&enumerator_)), "enumerator")) return false;
		endpoint_role_ = eMultimedia;
		HRESULT endpoint_result = enumerator_->GetDefaultAudioEndpoint(eRender, endpoint_role_, &device_);
		if (FAILED(endpoint_result)) {
			endpoint_role_ = eConsole;
			endpoint_result = enumerator_->GetDefaultAudioEndpoint(eRender, endpoint_role_, &device_);
		}
		if (!check(endpoint_result, "default speakers")) return false;
		LPWSTR device_id = nullptr;
		if (!check(device_->GetId(&device_id), "speaker identity")) return false;
		if (!device_id) return check(E_UNEXPECTED, "speaker identity");
		device_id_ = device_id;
		CoTaskMemFree(device_id);
		if (!check(device_->Activate(__uuidof(IAudioClient), CLSCTX_ALL, nullptr,
			reinterpret_cast<void **>(&client_)), "audio client")) return false;
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
		if (!check(client_->Initialize(AUDCLNT_SHAREMODE_SHARED, AUDCLNT_STREAMFLAGS_LOOPBACK,
			kBufferDuration, 0, format_, nullptr), "initialize loopback")) return false;
		UINT32 capacity = 0;
		if (!check(client_->GetBufferSize(&capacity), "buffer size")) return false;
		samples_.resize(capacity);
		if (!check(client_->GetService(__uuidof(IAudioCaptureClient), reinterpret_cast<void **>(&capture_)), "capture service")) return false;
		if (!check(client_->Start(), "start")) return false;
		sample_rate = format_->nSamplesPerSec;
		std::fprintf(stderr, "WASAPI speaker loopback: %lu Hz, %u channels\n", static_cast<unsigned long>(sample_rate), format_->nChannels);
		return true;
	}
	bool active() const { return capture_ != nullptr; }
	bool endpoint_changed()
	{
		if (!active() || !enumerator_ || device_id_.empty())
			return false;
		const auto now = std::chrono::steady_clock::now();
		if (now < next_endpoint_check_)
			return false;
		next_endpoint_check_ = now + std::chrono::milliseconds(500);

		IMMDevice *current_device = nullptr;
		HRESULT result = enumerator_->GetDefaultAudioEndpoint(eRender, endpoint_role_, &current_device);
		if (FAILED(result) && endpoint_role_ != eConsole) {
			result = enumerator_->GetDefaultAudioEndpoint(eRender, eConsole, &current_device);
		}
		if (FAILED(result)) {
			std::fprintf(stderr, "WASAPI default speaker query failed; reopening loopback\n");
			close();
			return true;
		}

		LPWSTR current_id = nullptr;
		result = current_device->GetId(&current_id);
		const bool changed = FAILED(result) || !current_id || device_id_ != current_id;
		if (current_id)
			CoTaskMemFree(current_id);
		current_device->Release();
		if (!changed)
			return false;
		std::fprintf(stderr, "WASAPI default speaker changed; reopening loopback\n");
		close();
		return true;
	}
	template<class Feed> bool pump(Feed feed)
	{
		if (!capture_) return false;
		// Bound the work per UI iteration, without retaining an unbounded queue.
		for (int packet = 0; packet < 32; ++packet) {
			UINT32 pending = 0;
			if (!check(capture_->GetNextPacketSize(&pending), "next packet")) return false;
			if (!pending) return true;
			BYTE *data = nullptr; UINT32 frames = 0; DWORD flags = 0;
			if (!check(capture_->GetBuffer(&data, &frames, &flags, nullptr, nullptr), "read packet")) return false;
			if (frames > samples_.size()) {
				capture_->ReleaseBuffer(frames);
				return check(E_UNEXPECTED, "packet larger than endpoint buffer");
			}
			if (diagnostics_)
				++diagnostic_packets_;
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
			// Release the OS capture buffer before potentially expensive DSP work.
			for (UINT32 frame = 0; frame < frames; ++frame) feed(samples_[frame]);
		}
		return true;
	}
};
#endif
