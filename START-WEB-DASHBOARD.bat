@echo off
chcp 65001 >nul
title NGỌC KHÁNH MEDIA - Web Dashboard
echo =======================================================
echo    ⚡ KHỞI ĐỘNG NGỌC KHÁNH MEDIA - WEB DASHBOARD
echo =======================================================
echo.
echo Đang mở Server Backend tại http://127.0.0.1:8088 ...
start "" http://127.0.0.1:8088
python backend\app.py
pause
