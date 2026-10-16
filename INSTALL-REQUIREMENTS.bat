@echo off
chcp 65001 >nul
title Cài đặt AutoVibe Matrix Dependencies
echo =======================================================
echo    ⚡ CÀI ĐẶT THƯ VIỆN CHO AUTOVIBE MATRIX
echo =======================================================
echo.
echo Đang cài đặt các thư viện Python cần thiết...
pip install -r requirements.txt
echo.
echo Đang tải trình duyệt Chromium cho Playwright...
playwright install chromium
echo.
echo =======================================================
echo    [✓] CÀI ĐẶT HOÀN TẤT! BẠN CÓ THỂ CHẠY HỆ THỐNG NGAY.
echo =======================================================
pause
