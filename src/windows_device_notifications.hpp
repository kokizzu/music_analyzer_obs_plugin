#pragma once

#if defined(_WIN32)

#include <dbt.h>
#include <windows.h>

#include <atomic>
#include <condition_variable>
#include <cstdint>
#include <cwchar>
#include <cstdio>
#include <mutex>
#include <string>
#include <thread>

// MIDI and BLE APIs do not expose a common arrival callback. A message-only
// window gives both workers prompt device-change wakeups while their existing
// timed retry remains the fallback for drivers that do not publish interfaces.
class WindowsDeviceNotifications {
public:
	WindowsDeviceNotifications(std::atomic<std::uint64_t> &generation,
					   std::condition_variable &wake)
		: generation_(generation), wake_(wake)
	{
	}

	~WindowsDeviceNotifications()
	{
		stop();
	}

	WindowsDeviceNotifications(const WindowsDeviceNotifications &) = delete;
	WindowsDeviceNotifications &operator=(const WindowsDeviceNotifications &) = delete;

	bool start()
	{
		if (thread_.joinable())
			return true;
		{
			std::lock_guard<std::mutex> lock(mutex_);
			stop_requested_ = false;
			ready_ = false;
			registered_ = false;
		}
		thread_ = std::thread(&WindowsDeviceNotifications::run, this);
		std::unique_lock<std::mutex> lock(mutex_);
		ready_condition_.wait(lock, [this]() { return ready_; });
		return registered_;
	}

	void stop()
	{
		HWND window = nullptr;
		{
			std::lock_guard<std::mutex> lock(mutex_);
			stop_requested_ = true;
			window = window_;
		}
		if (window)
			PostMessageW(window, WM_CLOSE, 0, 0);
		wake_.notify_all();
		if (thread_.joinable())
			thread_.join();
	}

private:
	static LRESULT CALLBACK window_proc(HWND window, UINT message, WPARAM wparam, LPARAM lparam)
	{
		WindowsDeviceNotifications *self = reinterpret_cast<WindowsDeviceNotifications *>(
			static_cast<LONG_PTR>(GetWindowLongPtrW(window, GWLP_USERDATA)));
		if (message == WM_NCCREATE) {
			const CREATESTRUCTW *create = reinterpret_cast<const CREATESTRUCTW *>(lparam);
			self = static_cast<WindowsDeviceNotifications *>(create->lpCreateParams);
			SetWindowLongPtrW(window, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(self));
		}
		if (!self)
			return DefWindowProcW(window, message, wparam, lparam);

		switch (message) {
		case WM_DEVICECHANGE:
			if (wparam == DBT_DEVICEARRIVAL || wparam == DBT_DEVICEREMOVECOMPLETE ||
			    wparam == DBT_DEVNODES_CHANGED || wparam == DBT_DEVICEREMOVEPENDING) {
				self->generation_.fetch_add(1, std::memory_order_release);
				self->wake_.notify_all();
			}
			return TRUE;
		case WM_CLOSE:
			DestroyWindow(window);
			return 0;
		case WM_DESTROY:
			PostQuitMessage(0);
			return 0;
		default:
			return DefWindowProcW(window, message, wparam, lparam);
		}
	}

	void run()
	{
		const HINSTANCE instance = GetModuleHandleW(nullptr);
		wchar_t class_name[96] = {};
		std::swprintf(class_name, sizeof(class_name) / sizeof(class_name[0]),
				      L"MusicAnalyzerDeviceNotifications_%lu_%p",
				      static_cast<unsigned long>(GetCurrentProcessId()), this);
		WNDCLASSEXW window_class = {};
		window_class.cbSize = sizeof(window_class);
		window_class.hInstance = instance;
		window_class.lpfnWndProc = &WindowsDeviceNotifications::window_proc;
		window_class.lpszClassName = class_name;
		const ATOM atom = RegisterClassExW(&window_class);
		if (!atom) {
			std::lock_guard<std::mutex> lock(mutex_);
			ready_ = true;
			ready_condition_.notify_all();
			return;
		}

		HWND window = CreateWindowExW(0, class_name, L"Music Analyzer device notifications", 0,
					     0, 0, 0, 0, HWND_MESSAGE, nullptr, instance, this);
		HDEVNOTIFY notification = nullptr;
		if (window) {
			DEV_BROADCAST_DEVICEINTERFACE_W filter = {};
			filter.dbcc_size = sizeof(filter);
			filter.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
			filter.dbcc_classguid = GUID_NULL;
			notification = RegisterDeviceNotificationW(window, &filter,
									   DEVICE_NOTIFY_WINDOW_HANDLE | DEVICE_NOTIFY_ALL_INTERFACE_CLASSES);
		}
		{
			std::lock_guard<std::mutex> lock(mutex_);
			window_ = window;
			registered_ = notification != nullptr;
			ready_ = true;
			ready_condition_.notify_all();
		}
		if (!notification)
			std::fprintf(stderr, "Windows device notifications unavailable; timed hardware retry remains active\n");

		MSG message = {};
		while (window && GetMessageW(&message, nullptr, 0, 0) > 0)
			DispatchMessageW(&message);

		if (notification)
			UnregisterDeviceNotification(notification);
		if (window)
			DestroyWindow(window);
		UnregisterClassW(class_name, instance);
		{
			std::lock_guard<std::mutex> lock(mutex_);
			window_ = nullptr;
		}
	}

	std::atomic<std::uint64_t> &generation_;
	std::condition_variable &wake_;
	std::thread thread_;
	std::mutex mutex_;
	std::condition_variable ready_condition_;
	HWND window_ = nullptr;
	bool stop_requested_ = false;
	bool ready_ = false;
	bool registered_ = false;
};

#endif
