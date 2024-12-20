# 影片壓縮工具

這是一個簡單的影片壓縮工具，使用 FFmpeg 作為核心引擎，提供圖形化介面讓使用者方便操作。

![image](https://github.com/yuuhouse/VideoCopresserV_02-potter-/blob/main/Screenshot.png)

## 功能特點

- 支援多種影片格式 (MP4, AVI, MKV, MOV)
- 使用 H.265 編碼器進行高效壓縮
- 可調整 CRF 值控制壓縮品質
- 自動記錄壓縮過程和結果
- 保留原檔案，產生新的壓縮檔案

## 使用說明

1. 點擊「Browse」按鈕選擇要壓縮的影片檔案
2. 設定 CRF 值（0-51）：
   - 數值越小 = 品質越好，檔案越大
   - 數值越大 = 品質越差，檔案越小
   - 建議值：23-28
3. 點擊「Compress」開始壓縮
4. 等待處理完成，壓縮後的檔案會自動儲存在原檔案相同目錄

## 系統需求

- Python 3.6 或更新版本
- FFmpeg（需要預先安裝）
- tkinter（Python GUI 套件）
- G++編譯器（如果要編譯 C++ 版本）

## 執行方式

### Python 版本
```bash
python video_compressor_gui.py
```

### C++ 版本
```bash
g++ video_compressor_gui.cpp -o video_compressor_gui.exe -std=c++17 -municode -mwindows -static -static-libgcc -static-libstdc++
```

## 注意事項

- 壓縮過程中請勿關閉程式
- 較大的檔案可能需要較長處理時間
- 所有壓縮記錄都會保存在 video_compression.log 檔案中
- 若出現異常狀況，可查看 log 檔案了解詳細資訊

## 錯誤排解

如果遇到以下問題：
1. 無法開啟程式
   - 確認是否已安裝 Python
   - 確認是否已安裝 FFmpeg 且加入系統路徑
2. 壓縮失敗
   - 檢查影片檔案是否完整
   - 確認硬碟空間是否足夠
   - 查看 log 檔案了解詳細錯誤訊息

## 檔案命名規則

壓縮後的檔案會依照以下格式命名：
```
原檔名_年月日_時分秒_compressed.副檔名
```
例如：`movie_20231225_153000_compressed.mp4`