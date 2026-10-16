@echo off
chcp 65001 >nul
title ĐẨY DỰ ÁN LÊN GITHUB MỚI
color 0B

echo ====================================================================
echo    ⚡ ĐẨY DỰ ÁN AUTO-MEDIA-MATRIX LÊN REPOSITORY GITHUB MỚI
echo ====================================================================
echo.
echo Bước 1: Mở trình duyệt vào link sau để tạo 1 Repository MỚI hoàn toàn:
echo 👉 https://github.com/new
echo (Đặt tên ví dụ: auto-media-matrix, chọn Public hoặc Private)
echo.
echo Bước 2: Dán đường link git repository vừa tạo vào dưới đây:
echo (Ví dụ: https://github.com/nguyenkhanh3122005/auto-media-matrix.git)
echo.

set /p REPO_URL="👉 Nhập link GitHub của bạn: "

if "%REPO_URL%"=="" (
    echo [!] Bạn chưa nhập link GitHub. Vui lòng chạy lại script!
    pause
    exit /b
)

echo.
echo [*] Đang cấu hình remote origin...
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo [*] Đang đẩy toàn bộ mã nguồn lên nhánh main...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ====================================================================
    echo    ✅ THÀNH CÔNG! DỰ ÁN ĐÃ ĐƯỢC TÁCH RIÊNG VÀ ĐẨY LÊN GITHUB!
    echo ====================================================================
    echo Bây giờ bạn có thể vào Vercel (https://vercel.com/new) và chọn
    echo repository mới này để deploy cực kỳ đơn giản!
) else (
    echo.
    echo [!] Quá trình đẩy lên GitHub gặp lỗi. Vui lòng kiểm tra lại link repo hoặc quyền truy cập.
)

echo.
pause
