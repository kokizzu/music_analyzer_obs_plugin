#include <dlfcn.h>
#include <onnxruntime_c_api.h>

#include <cstdio>
#include <cstdlib>
#include <vector>

namespace {

using GetApiBaseFn = const OrtApiBase *(ORT_API_CALL *)(void);

[[noreturn]] void fail(const char *message)
{
	std::fprintf(stderr, "basic_pitch_onnx_probe: %s\n", message);
	std::exit(1);
}

void check(const OrtApi *api, OrtStatus *status, const char *operation)
{
	if (!status)
		return;
	std::fprintf(stderr, "basic_pitch_onnx_probe: %s: %s\n", operation,
		     api->GetErrorMessage(status));
	api->ReleaseStatus(status);
	std::exit(1);
}

void print_tensor_shape(const OrtApi *api, OrtValue *value, const char *name)
{
	OrtTensorTypeAndShapeInfo *info = nullptr;
	check(api, api->GetTensorTypeAndShape(value, &info), "GetTensorTypeAndShape");
	size_t rank = 0;
	check(api, api->GetDimensionsCount(info, &rank), "GetDimensionsCount");
	std::vector<int64_t> dimensions(rank);
	check(api, api->GetDimensions(info, dimensions.data(), rank), "GetDimensions");
	std::printf("%s=", name);
	for (std::size_t i = 0; i < dimensions.size(); ++i)
		std::printf("%s%lld", i == 0 ? "" : "x", static_cast<long long>(dimensions[i]));
	std::printf("\n");
	api->ReleaseTensorTypeAndShapeInfo(info);
}

} // namespace

int main(int argc, char **argv)
{
	if (argc != 3)
		fail("usage: basic_pitch_onnx_probe ONNXRUNTIME_LIBRARY BASIC_PITCH_MODEL");

	void *library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
	if (!library)
		fail(dlerror());
	auto get_api_base = reinterpret_cast<GetApiBaseFn>(dlsym(library, "OrtGetApiBase"));
	if (!get_api_base)
		fail("OrtGetApiBase is missing from the ONNX Runtime library");
	const OrtApi *api = get_api_base()->GetApi(ORT_API_VERSION);
	if (!api)
		fail("incompatible ONNX Runtime C API");

	OrtEnv *environment = nullptr;
	OrtSessionOptions *options = nullptr;
	OrtSession *session = nullptr;
	OrtMemoryInfo *memory = nullptr;
	OrtValue *input = nullptr;
	OrtValue *outputs[3] = {nullptr, nullptr, nullptr};
	check(api, api->CreateEnv(ORT_LOGGING_LEVEL_WARNING, "music_analyzer_probe", &environment), "CreateEnv");
	check(api, api->CreateSessionOptions(&options), "CreateSessionOptions");
	check(api, api->SetIntraOpNumThreads(options, 1), "SetIntraOpNumThreads");
	check(api, api->CreateSession(environment, argv[2], options, &session), "CreateSession");
	check(api, api->CreateCpuMemoryInfo(OrtArenaAllocator, OrtMemTypeDefault, &memory), "CreateCpuMemoryInfo");

	std::vector<float> waveform(43844, 0.0f);
	const int64_t input_shape[] = {1, 43844, 1};
	check(api, api->CreateTensorWithDataAsOrtValue(memory, waveform.data(), waveform.size() * sizeof(float),
							 input_shape, 3, ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT, &input),
	      "CreateTensorWithDataAsOrtValue");
	const char *input_names[] = {"serving_default_input_2:0"};
	const char *output_names[] = {"StatefulPartitionedCall:1", "StatefulPartitionedCall:2",
				      "StatefulPartitionedCall:0"};
	check(api, api->Run(session, nullptr, input_names, &input, 1, output_names, 3, outputs), "Run");
	print_tensor_shape(api, outputs[0], "note");
	print_tensor_shape(api, outputs[1], "onset");
	print_tensor_shape(api, outputs[2], "contour");

	for (OrtValue *output : outputs)
		api->ReleaseValue(output);
	api->ReleaseValue(input);
	api->ReleaseMemoryInfo(memory);
	api->ReleaseSession(session);
	api->ReleaseSessionOptions(options);
	api->ReleaseEnv(environment);
	dlclose(library);
	return 0;
}
