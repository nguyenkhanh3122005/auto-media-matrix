@echo off
chcp 65001 >nul
title NGỌC KHÁNH MEDIA - Web Dashboard
echo =======================================================
echo    ⚡ KHỞI ĐỘNG NGỌC KHÁNH MEDIA - WEB DASHBOARD
echo    🌐 Giao diện: http://127.0.0.1:8000
echo =======================================================
echo.
echo Đang mở Server Backend tại http://127.0.0.1:8000 ...
start "" http://127.0.0.1:8000
python server.py
pause
