@echo off
chcp 65001 >nul
title KHỞI ĐỘNG DỰ ÁN TRÊN VISUAL STUDIO CODE
color 0A

echo ====================================================================
echo    ⚡ ĐANG MỞ DỰ ÁN NGỌC KHÁNH MEDIA TRÊN VISUAL STUDIO CODE...
echo ====================================================================
echo.
echo 📁 Thư mục dự án: %~dp0
echo.

where code >nul 2>nul
if %errorlevel% equ 0 (
    start "" code "%~dp0"
    echo [OK] Đã mở dự án trong VS Code thành công!
    echo 👉 Bạn chỉ cần nhấn phím [F5] trong VS Code để khởi chạy Server và mở giao diện.
) else (
    if exist "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" (
        start "" "%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe" "%~dp0"
        echo [OK] Đã mở dự án trong VS Code!
        echo 👉 Nhấn [F5] trong VS Code để chạy.
    ) else (
        echo [!] Không tìm thấy lệnh 'code' tự động.
        echo Vui lòng mở VS Code, chọn File -> Open Folder: %~dp0
    )
)

echo.
timeout /t 4 >nul
exit
