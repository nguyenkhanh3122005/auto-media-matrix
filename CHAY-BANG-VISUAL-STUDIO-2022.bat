@echo off
chcp 65001 >nul
title KHỞI ĐỘNG DỰ ÁN TRÊN VISUAL STUDIO 2022
color 0B

echo ====================================================================
echo    ⚡ ĐANG MỞ DỰ ÁN TRÊN VISUAL STUDIO 2022...
echo ====================================================================
echo.

set "VS_DIR=C:\Program Files\Microsoft Visual Studio\2022\Community\Common7\IDE"
if not exist "%VS_DIR%\devenv.exe" (
    set "VS_DIR=C:\Program Files\Microsoft Visual Studio\2022\Professional\Common7\IDE"
)
if not exist "%VS_DIR%\devenv.exe" (
    set "VS_DIR=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\Common7\IDE"
)

if exist "%VS_DIR%\devenv.exe" (
    start "" "%VS_DIR%\devenv.exe" "%~dp0"
    echo [OK] Đã mở dự án trong Visual Studio 2022!
    echo 👉 Nhấn [F5] để chạy dự án.
) else (
    echo [!] Không tìm thấy devenv.exe của VS 2022 ở đường dẫn mặc định.
    echo Đang mở qua VS Code hoặc mở trực tiếp Web Dashboard...
    start "" "%~dp0START-WEB-DASHBOARD.bat"
)

echo.
timeout /t 4 >nul
exit
