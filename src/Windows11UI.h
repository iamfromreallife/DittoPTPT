#pragma once

// Windows 11 desktop chrome for the existing Win32/MFC host.
// This is intentionally non-invasive: it does not replace controls, change
// window styles, redirect messages, or touch Ditto's clipboard handling.
// Unsupported DWM attributes return an error on older Windows versions.
#include <windows.h>
#include <dwmapi.h>
#include <uxtheme.h>
#include <commctrl.h>
#include <cwchar>
#pragma comment(lib, "dwmapi.lib")
#pragma comment(lib, "uxtheme.lib")
#pragma comment(lib, "advapi32.lib")

namespace DittoWindows11
{
	inline bool HighContrastEnabled()
	{
		HIGHCONTRASTW contrast = {};
		contrast.cbSize = sizeof(contrast);
		return ::SystemParametersInfoW(SPI_GETHIGHCONTRAST, sizeof(contrast), &contrast, 0) &&
			(contrast.dwFlags & HCF_HIGHCONTRASTON) != 0;
	}

	inline bool DarkAppsEnabled()
	{
		if (HighContrastEnabled())
			return false;
		DWORD lightTheme = 1;
		DWORD size = sizeof(lightTheme);
		const LSTATUS result = ::RegGetValueW(HKEY_CURRENT_USER,
			L"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
			L"AppsUseLightTheme", RRF_RT_REG_DWORD, nullptr, &lightTheme, &size);
		return result == ERROR_SUCCESS && lightTheme == 0;
	}

	inline void ApplyWindowChrome(HWND hWnd, bool mainWindow)
	{
		if (!::IsWindow(hWnd) || HighContrastEnabled())
			return;

		// Numeric attributes are the public Windows SDK DWM constants. Using
		// their values keeps the old v143/v145 project compatible with SDKs
		// older than the headers which introduced these enum names.
		const BOOL dark = DarkAppsEnabled() ? TRUE : FALSE;
		::DwmSetWindowAttribute(hWnd, static_cast<DWMWINDOWATTRIBUTE>(20), &dark, sizeof(dark)); // DWMWA_USE_IMMERSIVE_DARK_MODE

		const int round = 2; // DWMWCP_ROUND
		::DwmSetWindowAttribute(hWnd, static_cast<DWMWINDOWATTRIBUTE>(33), &round, sizeof(round)); // DWMWA_WINDOW_CORNER_PREFERENCE

		const COLORREF border = dark ? RGB(60, 60, 60) : RGB(225, 225, 225);
		::DwmSetWindowAttribute(hWnd, static_cast<DWMWINDOWATTRIBUTE>(34), &border, sizeof(border)); // DWMWA_BORDER_COLOR

		if (mainWindow)
		{
			const int mica = 2; // DWMSBT_MAINWINDOW
			::DwmSetWindowAttribute(hWnd, static_cast<DWMWINDOWATTRIBUTE>(38), &mica, sizeof(mica)); // DWMWA_SYSTEMBACKDROP_TYPE
		}
	}

	inline BOOL CALLBACK ModernizeChildControl(HWND child, LPARAM)
	{
		wchar_t name[64] = {};
		::GetClassNameW(child, name, static_cast<int>(_countof(name)));
		// Keep owner-drawn controls, editable content and custom scrollbars
		// untouched: they have their own behaviours and colour systems.
		if (_wcsicmp(name, WC_LISTVIEWW) == 0 ||
			_wcsicmp(name, WC_TREEVIEWW) == 0 ||
			_wcsicmp(name, L"ComboBox") == 0)
		{
			::SetWindowTheme(child, L"Explorer", nullptr);
		}
		return TRUE;
	}

	inline void ApplyDialogChrome(HWND hWnd)
	{
		ApplyWindowChrome(hWnd, true);
		::EnumChildWindows(hWnd, ModernizeChildControl, 0);
	}

	inline HHOOK& DialogHook()
	{
		static HHOOK hook = nullptr;
		return hook;
	}

	inline LRESULT CALLBACK OnDialogActivated(int code, WPARAM wParam, LPARAM lParam)
	{
		if (code == HCBT_ACTIVATE)
		{
			HWND hWnd = reinterpret_cast<HWND>(wParam);
			wchar_t className[64] = {};
			if (::IsWindow(hWnd) &&
				(::GetWindowLongPtr(hWnd, GWL_STYLE) & WS_CHILD) == 0 &&
				::GetClassNameW(hWnd, className, static_cast<int>(_countof(className))) &&
				::wcscmp(className, L"#32770") == 0)
			{
				ApplyDialogChrome(hWnd);
			}
		}
		return ::CallNextHookEx(DialogHook(), code, wParam, lParam);
	}

	inline void InstallDialogHook()
	{
		if (!DialogHook())
		{
			// UI-thread-only CBT hook: never inject code into other processes.
			DialogHook() = ::SetWindowsHookExW(WH_CBT, OnDialogActivated, nullptr, ::GetCurrentThreadId());
		}
	}

	inline void RemoveDialogHook()
	{
		if (DialogHook())
		{
			::UnhookWindowsHookEx(DialogHook());
			DialogHook() = nullptr;
		}
	}
}
