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

        elif path.endswith("/niches"):
            self.send_json({
                "cntt": {"name": "Công Nghệ Thông Tin & Lập Trình (CNTT)", "default_hook": "Đừng code thủ công nữa, xem ngay cách vibe code cực đỉnh này!"},
                "ecommerce": {"name": "Thương Mại Điện Tử & Thời Trang / Mỹ Phẩm", "default_hook": "Món đồ này vừa rẻ vừa xịn, tiếc là 90% mọi người chưa biết tới!"},
                "real_estate": {"name": "Bất Động Sản & Nhà Cửa / Thiết Kế", "default_hook": "Căn nhà này có thiết kế thông minh đến mức bạn sẽ muốn dọn vào ở ngay!"},
                "fnb": {"name": "Ẩm Thực & Nhà Hàng / Đồ Uống (F&B)", "default_hook": "Ai mê ăn uống tuyệt đối không được bỏ qua công thức thần thánh này!"},
                "finance": {"name": "Tài Chính & Đầu Tư / Kinh Doanh Online", "default_hook": "Nếu bạn muốn tự do tài chính trước tuổi 30, hãy khắc cốt ghi tâm bài học này!"},
                "education": {"name": "Giáo Dục & Tiếng Anh / Kỹ Năng Mềm", "default_hook": "Ngừng học vẹt ngay! Đây là cách học thông minh nhất mà trường học không dạy bạn."}
            })
            return

        elif path.endswith("/videos"):
            self.send_json([])
            return

        self.send_json({"status": "online", "message": "NGỌC KHÁNH MEDIA Vercel API is running"}, status=200)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if "auth/login" in path:
            self.send_json({
                "success": True,
                "user": {"id": 1, "username": "admin", "role": "admin", "full_name": "Quản Trị Viên Ngọc Khánh"}
            })
            return
        elif "auth/register" in path:
            self.send_json({
                "success": True,
                "message": "Đăng ký thành công! Hãy đăng nhập tài khoản của bạn."
            })
            return
        elif "toggle-active" in path:
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
        elif "ai-video/generate" in path:
            self.send_json({
                "success": True,
                "data": {
                    "niche_name": "Công Nghệ Thông Tin (CNTT)",
                    "title": "[CNTT] Vibe code web tự động chỉ bằng 1 câu lệnh",
                    "hook": "🔥 Đừng code thủ công nữa, xem ngay cách vibe code cực đỉnh này!",
                    "caption": "🔥 Đừng code thủ công nữa, xem ngay cách vibe code cực đỉnh này!\n\n👉 Vibe code web tự động.\n\nXem ngay bí kíp cực xịn trong video này nhé cả nhà! #vibecode #congnghe",
                    "hashtags": "#laptrinh #vibecode #congnghe #developer #ai #learncoding #codingtips",
                    "scenes": [
                        {"scene": 1, "duration": "0s - 3s (HOOK)", "visual": "Chữ giật tít lớn: Vibe code web phóng to", "voiceover": "Bạn có tin là việc tạo website bây giờ chỉ mất đúng 30 giây không?"},
                        {"scene": 2, "duration": "4s - 15s (VẤN ĐỀ & BÍ QUYẾT)", "visual": "Quay màn hình gõ câu lệnh prompt vào Antigravity", "voiceover": "Chỉ cần mô tả ý tưởng bằng tiếng Việt, AI sẽ tự động sinh toàn bộ code frontend và backend."},
                        {"scene": 3, "duration": "16s - 30s (GIÁ TRỊ)", "visual": "Giao diện web hoàn chỉnh hiện lên rực rỡ", "voiceover": "Giao diện siêu đẹp, đầy đủ tính năng và kết nối database chạy ngay tức khắc."},
                        {"scene": 4, "duration": "31s - 38s (CTA)", "visual": "Mũi tên chỉ xuống link Bio", "voiceover": "Bấm Lưu lại clip và Follow kênh để nhận full bộ prompt này nhé!"}
                    ],
                    "suggested_audio": "Nhạc nền Upbeat Trendy Lo-Fi",
                    "estimated_length": "38 giây",
                    "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
                    "file_size": "2.45 MB",
                    "md5_hash": "e9b20756a1b24890d98762514fcb7a12",
                    "resolution": "720x1280 (9:16)"
                }
            })
            return
        elif "channel/audit" in path:
            self.send_json({
                "success": True,
                "data": {
                    "channel_id": "@my_channel",
                    "platform": "TIKTOK",
                    "overall_score": 78,
                    "sub_scores": {"profile_optimization": 80, "content_retention": 74, "engagement_power": 80},
                    "status": "Tiềm Năng Cao - Cần Tối Ưu Hook & Bio",
                    "diagnosis": [
                        "✅ Định vị kênh khá tốt, phong cách thumbnail bắt đầu có sự đồng bộ.",
                        "⚠️ 3 giây đầu của video (Hook) cần giật tít mạnh hơn để giảm tỷ lệ rớt người xem.",
                        "💡 Nên gắn thêm link Bio thông minh để chuyển đổi người xem thành khách hàng tiềm năng."
                    ],
                    "actionable_steps": [
                        "1. Sửa Bio: Thêm lời kêu gọi hành động (CTA) bấm vào link quà tặng / Zalo.",
                        "2. Đổi 3s đầu clip: Đặt câu hỏi kích thích tò mò trước khi bắt đầu nội dung.",
                        "3. Đăng đều đặn vào 2 khung giờ vàng: 11:30 trưa và 19:45 tối."
                    ],
                    "content_pillars": [
                        {"pillar": "Video Phễu (Viral Hook)", "ratio": "50%", "purpose": "Hút tệp triệu view"},
                        {"pillar": "Video Chuyên Môn / Review", "ratio": "30%", "purpose": "Tạo uy tín chuyên gia"},
                        {"pillar": "Video Bán Hàng / Chuyển Đổi", "ratio": "20%", "purpose": "Chốt đơn sản phẩm"}
                    ]
                }
            })
            return
        elif "channel/growth-plan" in path:
            plan = []
            for d in range(1, 31):
                plan.append({
                    "day": d,
                    "week_theme": f"Tuần {min(4, (d-1)//7 + 1)}: Ma Trận Chuyển Đổi Khách Hàng",
                    "video_type": "Video Phễu" if d <= 7 else ("Video Chuyên Môn" if d <= 14 else ("Video Review" if d <= 21 else "Video Bán Hàng")),
                    "title": f"Bí quyết tối ưu sản phẩm đột phá (Ngày {d})",
                    "golden_hour": "11:30" if d % 2 == 0 else "19:45",
                    "cta_strategy": "Kêu gọi bấm vào link Bio nhận tài liệu / ưu đãi độc quyền"
                })
            self.send_json({"success": True, "data": plan})
            return
        elif "channel/target-nurture" in path:
            self.send_json({"success": True, "message": "Đã kích hoạt chế độ nuôi kênh mục tiêu chuyên sâu theo ngách!"})
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
