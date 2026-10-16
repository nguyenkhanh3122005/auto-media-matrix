@echo off
chcp 65001 >nul
title NGỌC KHÁNH MEDIA - FastAPI Server (Port 8000)
color 0B

echo ====================================================================
echo    ⚡ KHỞI ĐỘNG NGỌC KHÁNH MEDIA - FASTAPI AI AUTOMATION SERVER
echo ====================================================================
echo.
echo 🌐 Đang mở Web Dashboard tại http://127.0.0.1:8000 ...
echo 📡 WebSocket Live Streaming: ws://127.0.0.1:8000/ws/logs
echo.

start "" http://127.0.0.1:8000
python server.py
pause
