from http.server import BaseHTTPRequestHandler
import json
import os
from urllib.parse import urlparse, parse_qs

# Dữ liệu mẫu mô phỏng trên Vercel Serverless
DEMO_ACCOUNTS = [
    {
        "id": 1,
        "name": "(FB): nguyễn duy",
        "platform": "facebook",
        "method": "browser",
        "proxy": "Dùng IP máy / 50ms",
        "status": "idle",
        "is_enabled": 1,
        "actions_count": 0,
        "followers_count": 0,
        "created_at": "1/10/2026"
    },
    {
        "id": 2,
        "name": "(YTB): QUETUDUY",
        "platform": "youtube",
        "method": "browser",
        "proxy": "Dùng IP máy / 50ms",
        "status": "idle",
        "is_enabled": 1,
        "actions_count": 0,
        "followers_count": 0,
        "created_at": "25/9/2026"
    },
    {
        "id": 3,
        "name": "(TT): hgboo213",
        "platform": "tiktok",
        "method": "browser",
        "proxy": "Dùng IP máy / 50ms",
        "status": "idle",
        "is_enabled": 1,
        "actions_count": 0,
        "followers_count": 0,
        "created_at": "1/10/2026"
    },
    {
        "id": 4,
        "name": "(FB): quetuduy",
        "platform": "facebook",
        "method": "browser",
        "proxy": "Dùng IP máy / 50ms",
        "status": "idle",
        "is_enabled": 1,
        "actions_count": 0,
        "followers_count": 0,
        "created_at": "25/9/2026"
    },
    {
        "id": 5,
        "name": "(TT): quetuduy",
        "platform": "tiktok",
        "method": "browser",
        "proxy": "Dùng IP máy / 50ms",
        "status": "idle",
        "is_enabled": 1,
        "actions_count": 0,
        "followers_count": 0,
        "created_at": "28/9/2026"
    }
]

DEMO_LOGS = [
    {"timestamp": "12:00:00", "status": "success", "account_name": "System", "action": "Khởi động Vercel", "details": "Hệ thống BAOX AI đang chạy trên Vercel Serverless"},
    {"timestamp": "12:00:05", "status": "info", "account_name": "(TT): quetuduy", "action": "Sẵn sàng", "details": "Profile Chrome Stealth đã đồng bộ"}
]

class handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        content = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path.endswith("/accounts"):
            self.send_json(DEMO_ACCOUNTS)
            return

        elif path.endswith("/stats"):
            self.send_json({
                "total_accounts": len(DEMO_ACCOUNTS),
                "running_accounts": 0,
                "total_videos": 5,
                "uploaded_videos": 3,
                "total_actions": 48
            })
            return

        elif path.endswith("/logs"):
            self.send_json(DEMO_LOGS)
            return

        elif path.endswith("/proxies"):
            self.send_json([
                {"id": 1, "proxy_str": "103.149.28.14:8080", "status": "live", "latency_ms": 38, "ip_location": "Việt Nam - VNPT"},
                {"id": 2, "proxy_str": "14.225.205.81:8080", "status": "live", "latency_ms": 42, "ip_location": "Việt Nam - Viettel"},
                {"id": 3, "proxy_str": "104.28.192.5:3128", "status": "live", "latency_ms": 65, "ip_location": "United States (US)"}
            ])
            return

        elif path.endswith("/schedules"):
            self.send_json([
                {"id": 1, "platform": "tiktok", "time_slot": "11:30 (Trưa)", "status": "active"},
                {"id": 2, "platform": "facebook", "time_slot": "19:45 (Tối)", "status": "active"}
            ])
            return

        elif path.endswith("/videos"):
            self.send_json([])
            return

        self.send_json({"status": "online", "message": "BAOX AI Vercel API is running"}, status=200)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if "toggle-active" in path:
            self.send_json({"success": True, "message": "Đã đổi trạng thái trên Cloud"})
            return
        elif "toggle-all" in path:
            self.send_json({"success": True, "message": "Đã cập nhật toàn bộ kênh"})
            return
        elif "batch-import" in path:
            self.send_json({"success": True, "count": 3, "message": "Đã nhập tài khoản thành công"})
            return
        elif "proxies" in path:
            self.send_json({"success": True, "message": "Đã thêm Proxy Stealth"})
            return
        elif "schedules" in path:
            self.send_json({"success": True, "message": "Đã lên lịch up tự động"})
            return
        elif "logs/clear" in path:
            self.send_json({"success": True, "message": "Đã làm sạch nhật ký"})
            return
        elif "open-login" in path:
            self.send_json({"success": True, "message": "Vui lòng mở ứng dụng trên máy tính cục bộ để mở trình duyệt Chrome vật lý!"})
            return
        elif "check-alive" in path:
            self.send_json({"success": True, "status": "online", "message": "Kênh hoạt động bình thường"})
            return
        elif "nurture-batch" in path:
            self.send_json({"success": True, "message": "Đã phát lệnh nuôi hàng loạt tới các máy Client kết nối!"})
            return
        elif "stop-all" in path:
            self.send_json({"success": True, "message": "Đã dừng toàn bộ"})
            return

        self.send_json({"success": True, "message": "Tác vụ đã được ghi nhận"})
