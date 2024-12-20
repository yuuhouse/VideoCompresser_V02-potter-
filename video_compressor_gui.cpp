#include <windows.h>
#include <commdlg.h>
#include <string>
#include <iostream>
#include <cstdlib>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <sstream>

void compressVideo(const std::wstring& inputFilePath, const std::wstring& outputFilePath, int crf) {
    std::wstring command = L"ffmpeg -i \"" + inputFilePath + L"\" -vcodec libx264 -crf " + std::to_wstring(crf) + L" \"" + outputFilePath + L"\"";
    std::wcout << L"Running command: " << command << std::endl;
    int result = _wsystem(command.c_str());

    if (result != 0) {
        std::wcerr << L"Error: Failed to compress video. Command: " << command << std::endl;
        std::wcerr << L"FFmpeg exited with code " << result << std::endl;
        exit(EXIT_FAILURE);
    }

    auto file_size = std::filesystem::file_size(outputFilePath);
    std::wcout << L"Compressed file size: " << file_size / (1024 * 1024) << L" MB" << std::endl;
}

std::wstring openFileDialog(HWND hwnd) {
    OPENFILENAMEW ofn;
    wchar_t szFile[260] = { 0 };
    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFile = szFile;
    ofn.nMaxFile = sizeof(szFile) / sizeof(wchar_t);
    ofn.lpstrFilter = L"All Files\0*.*\0";
    ofn.nFilterIndex = 1;
    ofn.Flags = OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST;

    if (GetOpenFileNameW(&ofn) == TRUE) {
        return std::wstring(ofn.lpstrFile);
    }
    return L"";
}

std::wstring generateOutputPath(const std::wstring& inputPath) {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    std::wstringstream ss;
    std::wstring extension = L".mp4";
    
    // 從輸入路徑中提取目錄和文件名
    std::filesystem::path path(inputPath);
    auto parent_path = path.parent_path();
    auto stem = path.stem();
    
    // 格式化時間戳記
    ss << std::put_time(std::localtime(&in_time_t), L"_%Y%m%d_%H%M%S");
    
    // 組合新的輸出路徑
    return (parent_path / (stem.wstring() + ss.str() + extension)).wstring();
}

LRESULT CALLBACK WindowProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
    static HWND hInputButton, hCrfEdit, hCompressButton;
    static std::wstring inputFilePath;

    switch (uMsg) {
    case WM_CREATE:
        hInputButton = CreateWindowW(L"BUTTON", L"Select Input File", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            20, 20, 150, 30, hwnd, (HMENU)1, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);
        CreateWindowW(L"STATIC", L"CRF Value (0-51):", WS_VISIBLE | WS_CHILD,
            20, 60, 150, 20, hwnd, NULL, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);
        hCrfEdit = CreateWindowW(L"EDIT", L"", WS_TABSTOP | WS_VISIBLE | WS_CHILD | WS_BORDER | ES_NUMBER,
            180, 60, 50, 20, hwnd, NULL, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);
        hCompressButton = CreateWindowW(L"BUTTON", L"Compress Video", WS_TABSTOP | WS_VISIBLE | WS_CHILD | BS_DEFPUSHBUTTON,
            20, 100, 150, 30, hwnd, (HMENU)3, (HINSTANCE)GetWindowLongPtr(hwnd, GWLP_HINSTANCE), NULL);
        break;
    case WM_COMMAND:
        if (LOWORD(wParam) == 1) {
            inputFilePath = openFileDialog(hwnd);
        }
        else if (LOWORD(wParam) == 3) {
            wchar_t crfText[4];
            GetWindowTextW(hCrfEdit, crfText, 4);
            int crf = _wtoi(crfText);
            if (!inputFilePath.empty() && crf >= 0 && crf <= 51) {
                std::wstring outputFilePath = generateOutputPath(inputFilePath);
                compressVideo(inputFilePath, outputFilePath, crf);
                MessageBoxW(hwnd, L"Video compression completed successfully.", L"Success", MB_OK);
            }
            else {
                MessageBoxW(hwnd, L"Please select valid input file and CRF value.", L"Error", MB_OK | MB_ICONERROR);
            }
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        break;
    default:
        return DefWindowProc(hwnd, uMsg, wParam, lParam);
    }
    return 0;
}

int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPWSTR lpCmdLine, int nCmdShow) {
    const wchar_t CLASS_NAME[] = L"VideoCompressorWindowClass";

    WNDCLASSW wc = {};
    wc.lpfnWndProc = WindowProc;
    wc.hInstance = hInstance;
    wc.lpszClassName = CLASS_NAME;

    RegisterClassW(&wc);

    HWND hwnd = CreateWindowExW(
        0,
        CLASS_NAME,
        L"Video Compressor",
        WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 400, 250,
        NULL,
        NULL,
        hInstance,
        NULL
    );

    if (hwnd == NULL) {
        return 0;
    }

    ShowWindow(hwnd, nCmdShow);

    MSG msg = {};
    while (GetMessage(&msg, NULL, 0, 0)) {
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return 0;
}
