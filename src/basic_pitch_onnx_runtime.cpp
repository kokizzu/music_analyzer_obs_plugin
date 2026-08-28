#include "basic_pitch_onnx_runtime.hpp"

#if defined(__ANDROID__)

namespace mao {

BasicPitchOnnxRuntime::~BasicPitchOnnxRuntime()
{
	reset();
}

bool BasicPitchOnnxRuntime::check_status(void *, const char *)
{
	last_error_ = "ONNX Runtime is unavailable in this Android build";
	return false;
}

void BasicPitchOnnxRuntime::reset()
{
	library_ = nullptr;
	api_ = nullptr;
	environment_ = nullptr;
	session_options_ = nullptr;
	session_ = nullptr;
}

bool BasicPitchOnnxRuntime::load(const char *, const char *)
{
	reset();
	last_error_ = "ONNX Runtime is unavailable in this Android build";
	return false;
}

bool BasicPitchOnnxRuntime::infer(const float *, std::size_t, BasicPitchOnnxOutput &)
{
	last_error_ = "ONNX Runtime is unavailable in this Android build";
	return false;
}

} // namespace mao

#else

#include <dlfcn.h>
#include <onnxruntime_c_api.h>

#include <algorithm>
#include <cstdio>

namespace mao {
namespace {

using GetApiBaseFn = const OrtApiBase *(ORT_API_CALL *)(void);

const OrtApi *as_api(const void *api)
{
	return static_cast<const OrtApi *>(api);
}

template <typename T> T *as(void *value)
{
	return static_cast<T *>(value);
}

} // namespace

BasicPitchOnnxRuntime::~BasicPitchOnnxRuntime()
{
	reset();
}

bool BasicPitchOnnxRuntime::check_status(void *opaque_status, const char *operation)
{
	OrtStatus *status = as<OrtStatus>(opaque_status);
	if (!status)
		return true;
	const OrtApi *api = as_api(api_);
	last_error_ = operation;
	last_error_ += ": ";
	last_error_ += api ? api->GetErrorMessage(status) : "ONNX Runtime status unavailable";
	if (api)
		api->ReleaseStatus(status);
	return false;
}

void BasicPitchOnnxRuntime::reset()
{
	const OrtApi *api = as_api(api_);
	if (api && session_)
		api->ReleaseSession(as<OrtSession>(session_));
	if (api && session_options_)
		api->ReleaseSessionOptions(as<OrtSessionOptions>(session_options_));
	if (api && environment_)
		api->ReleaseEnv(as<OrtEnv>(environment_));
	session_ = nullptr;
	session_options_ = nullptr;
	environment_ = nullptr;
	api_ = nullptr;
	if (library_)
		dlclose(library_);
	library_ = nullptr;
}

bool BasicPitchOnnxRuntime::load(const char *runtime_library_path, const char *model_path)
{
	reset();
	last_error_.clear();
	if (!runtime_library_path || !*runtime_library_path || !model_path || !*model_path) {
		last_error_ = "runtime library and model paths are required";
		return false;
	}
	library_ = dlopen(runtime_library_path, RTLD_NOW | RTLD_LOCAL);
	if (!library_) {
		last_error_ = dlerror();
		return false;
	}
	auto get_api_base = reinterpret_cast<GetApiBaseFn>(dlsym(library_, "OrtGetApiBase"));
	if (!get_api_base) {
		last_error_ = "OrtGetApiBase is missing from the ONNX Runtime library";
		reset();
		return false;
	}
	api_ = get_api_base()->GetApi(ORT_API_VERSION);
	if (!api_) {
		last_error_ = "incompatible ONNX Runtime C API";
		reset();
		return false;
	}
	const OrtApi *api = as_api(api_);
	OrtEnv *environment = nullptr;
	OrtSessionOptions *options = nullptr;
	OrtSession *session = nullptr;
	if (!check_status(api->CreateEnv(ORT_LOGGING_LEVEL_WARNING, "music_analyzer", &environment), "CreateEnv") ||
	    !check_status(api->CreateSessionOptions(&options), "CreateSessionOptions") ||
	    !check_status(api->SetIntraOpNumThreads(options, 1), "SetIntraOpNumThreads") ||
	    !check_status(api->CreateSession(environment, model_path, options, &session), "CreateSession")) {
		environment_ = environment;
		session_options_ = options;
		session_ = session;
		reset();
		return false;
	}
	environment_ = environment;
	session_options_ = options;
	session_ = session;
	return true;
}

bool BasicPitchOnnxRuntime::infer(const float *waveform, std::size_t count, BasicPitchOnnxOutput &output)
{
	last_error_.clear();
	if (!ready() || !waveform || count != kInputSamples) {
		last_error_ = "runtime is not ready or waveform shape is invalid";
		return false;
	}
	const OrtApi *api = as_api(api_);
	OrtMemoryInfo *memory = nullptr;
	OrtValue *input = nullptr;
	OrtValue *outputs[3] = {nullptr, nullptr, nullptr};
	const int64_t input_shape[] = {1, static_cast<int64_t>(kInputSamples), 1};
	const char *input_names[] = {"serving_default_input_2:0"};
	const char *output_names[] = {"StatefulPartitionedCall:1", "StatefulPartitionedCall:2",
				      "StatefulPartitionedCall:0"};
	const std::size_t expected_sizes[] = {
		BasicPitchOnnxOutput::kFrames * BasicPitchOnnxOutput::kNoteBins,
		BasicPitchOnnxOutput::kFrames * BasicPitchOnnxOutput::kNoteBins,
		BasicPitchOnnxOutput::kFrames * BasicPitchOnnxOutput::kContourBins,
	};
	std::vector<float> *destinations[] = {&output.note, &output.onset, &output.contour};
	bool ok = check_status(api->CreateCpuMemoryInfo(OrtArenaAllocator, OrtMemTypeDefault, &memory),
			       "CreateCpuMemoryInfo") &&
		  check_status(api->CreateTensorWithDataAsOrtValue(memory, const_cast<float *>(waveform),
							      count * sizeof(float), input_shape, 3,
							      ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT, &input),
			       "CreateTensorWithDataAsOrtValue") &&
		  check_status(api->Run(as<OrtSession>(session_), nullptr, input_names, &input, 1, output_names, 3,
					outputs),
			       "Run");
	for (std::size_t i = 0; ok && i < 3; ++i) {
		float *data = nullptr;
		ok = check_status(api->GetTensorMutableData(outputs[i], reinterpret_cast<void **>(&data)),
				  "GetTensorMutableData");
		if (ok)
			destinations[i]->assign(data, data + expected_sizes[i]);
	}
	for (OrtValue *value : outputs) {
		if (value)
			api->ReleaseValue(value);
	}
	if (input)
		api->ReleaseValue(input);
	if (memory)
		api->ReleaseMemoryInfo(memory);
	return ok;
}

} // namespace mao

#endif
