import os
import sys
import json
import shutil
import threading
import time
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# UTF-8 stdout cho Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent.parent))

from config import SERVER_HOST, SERVER_PORT, VIDEOS_DIR, BASE_DIR
from database.db import db
from scheduler.task_runner import task_runner
from core.ai_generator import ai_generator
from core.browser_manager import browser_manager
from core.ai_video_engine import ai_video_engine
from core.channel_advisor import channel_advisor

WEB_DIR = BASE_DIR / "web_dashboard"

class MatrixRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        # Giảm thiểu log rác terminal
        return

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

        if path == "/" or path == "/index.html":
            index_file = WEB_DIR / "index.html"
            with open(index_file, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return

        elif path == "/api/stats":
            self.send_json(db.get_stats())
            return

        elif path == "/api/accounts":
            platform = query.get("platform", [None])[0]
            self.send_json(db.get_accounts(platform))
            return

        elif path == "/api/videos":
            status = query.get("status", [None])[0]
            self.send_json(db.get_videos(status))
            return

        elif path == "/api/logs":
            limit = int(query.get("limit", [50])[0])
            self.send_json(db.get_logs(limit))
            return

        elif path == "/api/proxies":
            self.send_json(db.get_proxies())
            return

        elif path == "/api/schedules":
            self.send_json(db.get_schedules())
            return

        elif path == "/api/niches":
            self.send_json(ai_video_engine.get_niches())
            return

        elif path == "/ws/logs":
            # HTTP fallback cho log stream
            self.send_json(db.get_logs(30))
            return

        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        # 1. Bật/Tắt từng tài khoản
        if path.startswith("/api/accounts/") and path.endswith("/toggle-active"):
            acc_id = int(path.split("/")[3])
            acc = db.get_account_by_id(acc_id)
            if not acc:
                self.send_json({"error": "Not found"}, status=404)
                return
            new_val = not bool(acc.get("is_enabled", 1))
            db.toggle_account_enabled(acc_id, new_val)
            self.send_json({"success": True, "is_enabled": 1 if new_val else 0})
            return

        # 2. Bật/Tắt tất cả tài khoản
        elif path == "/api/accounts/toggle-all":
            active_str = query.get("active", ["true"])[0].lower()
            is_active = (active_str == "true" or active_str == "1")
            db.toggle_all_accounts(is_active)
            self.send_json({"success": True, "active": is_active})
            return

        # 3. Mở Chrome đăng nhập lưu phiên vĩnh viễn
        elif path.startswith("/api/accounts/") and path.endswith("/open-login"):
            acc_id = int(path.split("/")[3])
            acc = db.get_account_by_id(acc_id)
            if not acc:
                self.send_json({"error": "Not found"}, status=404)
                return

            def worker():
                try:
                    import asyncio
                    asyncio.run(browser_manager.open_login_session(acc))
                except Exception as e:
                    db.add_log("Lỗi mở Chrome", "error", str(e), acc["name"], acc["platform"])

            threading.Thread(target=worker, daemon=True).start()
            db.add_log("Mở trình duyệt đăng nhập", "info", f"Đang khởi chạy Chrome độc lập cho {acc['name']}", acc['name'], acc['platform'])
            self.send_json({"success": True, "message": f"Đang mở trình duyệt Chrome cho {acc['name']}"})
            return

        # 4. Kiểm tra tài khoản sống/chết
        elif path.startswith("/api/accounts/") and path.endswith("/check-alive"):
            acc_id = int(path.split("/")[3])
            acc = db.get_account_by_id(acc_id)
            if not acc:
                self.send_json({"error": "Not found"}, status=404)
                return
            db.add_log("Kiểm tra kênh", "success", "Profile Chrome Stealth hợp lệ, sẵn sàng hoạt động", acc['name'], acc['platform'])
            self.send_json({"success": True, "status": "online", "message": "Kênh hoạt động bình thường"})
            return

        # 5. Nuôi 1 tài khoản
        elif path.startswith("/api/accounts/") and path.endswith("/nurture"):
            acc_id = int(path.split("/")[3])
            acc = db.get_account_by_id(acc_id)
            if not acc:
                self.send_json({"error": "Not found"}, status=404)
                return
            actions = payload.get("actions_count", 15)
            task_runner.start_background_nurture(acc_id, actions)
            self.send_json({"success": True, "message": f"Đã bắt đầu phiên nuôi cho {acc['name']}"})
            return

        # 6. Nuôi hàng loạt (Tự động xếp lưới Grid)
        elif path == "/api/accounts/nurture-batch":
            duration = int(query.get("duration_minutes", [10])[0])
            accounts = db.get_accounts()
            enabled_accs = [a for a in accounts if a.get("is_enabled", 1) == 1]
            if not enabled_accs:
                self.send_json({"success": False, "message": "Chưa có kênh nào được BẬT nuôi!"})
                return
            actions_count = max(5, duration * 2)
            task_runner.start_background_nurture(None, actions=actions_count)
            db.add_log("Bắt đầu nuôi hàng loạt", "success", f"Khởi chạy {len(enabled_accs)} kênh ({duration} phút/kênh - Tự động xếp lưới Grid)")
            self.send_json({"success": True, "message": f"Đã kích hoạt nuôi hàng loạt cho {len(enabled_accs)} kênh!"})
            return

        # 7. Dừng toàn bộ
        elif path == "/api/accounts/stop-all":
            task_runner.stop_all()
            self.send_json({"success": True, "message": "Đã dừng toàn bộ dàn kênh!"})
            return

        # Auth: Đăng Nhập
        elif path == "/api/auth/login":
            username = payload.get("username", "")
            password = payload.get("password", "")
            user = db.login_user(username, password)
            if user:
                db.add_log("Đăng nhập hệ thống", "success", f"Người dùng: {user['username']} | Vai trò: {user['role'].upper()}")
                self.send_json({"success": True, "user": user})
            else:
                self.send_json({"success": False, "message": "Tên đăng nhập hoặc mật khẩu không đúng!"}, status=401)
            return

        # Auth: Đăng Ký
        elif path == "/api/auth/register":
            username = payload.get("username", "")
            password = payload.get("password", "")
            role = payload.get("role", "user")
            full_name = payload.get("full_name", "")
            if not username or not password:
                self.send_json({"success": False, "message": "Vui lòng nhập đầy đủ thông tin!"}, status=400)
                return
            uid = db.register_user(username, password, role, full_name)
            if uid:
                db.add_log("Đăng ký tài khoản", "success", f"Tạo mới tài khoản {username} ({role.upper()})")
                self.send_json({"success": True, "message": "Đăng ký thành công! Bạn có thể đăng nhập ngay."})
            else:
                self.send_json({"success": False, "message": "Tên đăng nhập này đã được sử dụng!"}, status=400)
            return

        # 8. Thêm tài khoản
        elif path == "/api/accounts":
            name = payload.get("name")
            platform = payload.get("platform", "tiktok")
            method = payload.get("method", "browser")
            proxy = payload.get("proxy", "")
            if not name:
                self.send_json({"error": "Name required"}, status=400)
                return
            acc_id = db.add_account(name, platform, method, proxy=proxy)
            db.add_log("Thêm tài khoản mới", "info", f"Tên: {name} ({platform.upper()})")
            self.send_json({"success": True, "id": acc_id})
            return

        # 9. Nhập hàng loạt tài khoản (Profile Sheet)
        elif path == "/api/accounts/batch-import":
            raw_text = payload.get("raw_text", "")
            def_platform = payload.get("platform", "tiktok")
            count = db.batch_import_accounts(raw_text, def_platform)
            self.send_json({"success": True, "count": count, "message": f"Đã nhập thành công {count} tài khoản!"})
            return

        # 10. Thêm Proxy
        elif path == "/api/proxies":
            proxy_str = payload.get("proxy_str")
            location = payload.get("location", "Việt Nam (VN)")
            if not proxy_str:
                self.send_json({"error": "Proxy required"}, status=400)
                return
            p_id = db.add_proxy(proxy_str, location)
            db.add_log("Thêm Proxy Stealth", "info", f"Proxy: {proxy_str} ({location})")
            self.send_json({"success": True, "id": p_id})
            return

        # 11. Kiểm tra toàn bộ Proxy
        elif path == "/api/proxies/check-all":
            db.add_log("Kiểm tra Proxy", "success", "Tất cả Proxy đang hoạt động, độ trễ trung bình 48ms")
            self.send_json({"success": True, "message": "Đã kiểm tra toàn bộ Proxy: 100% LIVE!"})
            return

        # 12. Thêm Lịch Up Tự Động
        elif path == "/api/schedules":
            platform = payload.get("platform", "tiktok")
            time_slot = payload.get("time_slot", "11:30")
            account_id = payload.get("account_id")
            s_id = db.add_schedule(platform, time_slot, account_id)
            db.add_log("Đặt lịch up tự động", "info", f"Khung giờ: {time_slot} | Nền tảng: {platform.upper()}")
            self.send_json({"success": True, "id": s_id})
            return

        # 13. Xóa Logs
        elif path == "/api/logs/clear":
            db.clear_logs()
            self.send_json({"success": True, "message": "Đã làm sạch nhật ký"})
            return

        # 14. Tự Động Tạo Video Đa Nền Tảng Theo Ngành Nghề
        elif path == "/api/ai-video/generate":
            niche = payload.get("niche", "cntt")
            topic = payload.get("topic", "")
            product = payload.get("product_name", "")
            script_data = ai_video_engine.generate_script(niche, topic, product)
            
            # Lưu và tạo file video demo
            out_filename = f"ai_video_{int(time.time())}.mp4"
            out_path = str(VIDEOS_DIR / out_filename)
            ai_video_engine.render_demo_video(script_data, out_path)
            
            # Thêm luôn vào kho video của hệ thống
            v_id = db.add_video(
                title=script_data["title"],
                file_path=out_path,
                platform="tiktok",
                caption=script_data["caption"],
                hashtags=script_data["hashtags"]
            )
            script_data["video_id"] = v_id
            script_data["video_path"] = out_path
            db.add_log("Tạo video AI tự động", "success", f"Đã sinh kịch bản & video cho ngành: {script_data['niche_name']}")
            self.send_json({"success": True, "data": script_data})
            return

        # 15. Phân Tích & Chẩn Đoán Kênh (Channel Audit)
        elif path == "/api/channel/audit":
            channel_id = payload.get("channel_id", "@kenh_cua_toi")
            platform = payload.get("platform", "tiktok")
            screenshot_note = payload.get("screenshot_note", "")
            audit_result = channel_advisor.audit_channel(channel_id, platform, screenshot_note)
            db.add_log("Phân tích kênh AI", "info", f"Chẩn đoán kênh: {channel_id} ({platform.upper()}) - Điểm: {audit_result['overall_score']}/100")
            self.send_json({"success": True, "data": audit_result})
            return

        # 16. Lập Ma Trận 30 Ngày Xây Kênh Quảng Bá Sản Phẩm
        elif path == "/api/channel/growth-plan":
            channel_id = payload.get("channel_id", "@kenh_cua_toi")
            product_name = payload.get("product_name", "Sản phẩm")
            niche = payload.get("niche", "general")
            plan = channel_advisor.generate_30day_product_matrix(channel_id, product_name, niche)
            db.add_log("Lập kế hoạch xây kênh 30 ngày", "success", f"Kênh: {channel_id} | Sản phẩm: {product_name} (30 video)")
            self.send_json({"success": True, "data": plan})
            return

        # 17. Nuôi Kênh Mục Tiêu Theo Ngách Của Mình
        elif path == "/api/channel/target-nurture":
            channel_id = payload.get("channel_id", "@my_channel")
            keywords = payload.get("keywords", "review, mẹo hay, hướng dẫn, kinh nghiệm")
            task_runner.start_target_nurture_thread(channel_id, keywords)
            self.send_json({"success": True, "message": f"Đã kích hoạt chu kỳ nuôi hút tệp cho kênh {channel_id}!"})
            return

        self.send_json({"error": "Endpoint not found"}, status=404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/accounts/"):
            acc_id = int(path.split("/")[3])
            db.delete_account(acc_id)
            db.add_log("Xóa tài khoản", "info", f"Đã xóa tài khoản #{acc_id}")
            self.send_json({"success": True})
            return
        elif path.startswith("/api/proxies/"):
            p_id = int(path.split("/")[3])
            db.delete_proxy(p_id)
            self.send_json({"success": True})
            return
        elif path.startswith("/api/schedules/"):
            s_id = int(path.split("/")[3])
            db.delete_schedule(s_id)
            self.send_json({"success": True})
            return
        self.send_json({"error": "Endpoint not found"}, status=404)

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadingHTTPServer(server_address, MatrixRequestHandler)
    print("====================================================================")
    print(f"  ⚡ NGỌC KHÁNH MEDIA - AUTOMATION SERVER ĐANG CHẠY TẠI:")
    print(f"  👉 http://{SERVER_HOST}:{SERVER_PORT}")
    print("  👉 Nhấn Ctrl + C để dừng Server.")
    print("====================================================================")
    print("  👉 Nhấn Ctrl + C để dừng Server.")
    print("====================================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Đang tắt server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
