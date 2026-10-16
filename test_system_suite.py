import os
import sys
import json
import time
import socket
import urllib.request
import urllib.error

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8000"

def request_api(method: str, path: str, body: dict = None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            try:
                res_json = json.loads(content)
            except Exception:
                res_json = content[:100]
            return resp.status, True, res_json
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8", errors="replace")
        return e.code, False, content
    except Exception as e:
        return 0, False, str(e)

def run_suite():
    print("\n" + "=" * 70)
    print("  🚀 BẮT ĐẦU TEST TỰ ĐỘNG TOÀN DIỆN HỆ THỐNG NGỌC KHÁNH MEDIA")
    print(f"  Target: {BASE_URL}")
    print("=" * 70 + "\n")

    test_cases = []
    
    # 1. UI Root & Favicon
    test_cases.append(("GET", "/", None, [200], "Giao diện Web Dashboard"))
    test_cases.append(("GET", "/favicon.ico", None, [204, 200], "Favicon (204 No Content)"))

    # 2. Accounts API
    test_cases.append(("GET", "/api/accounts", None, [200], "Lấy danh sách kênh"))
    test_cases.append(("POST", "/api/accounts", {"name": f"acc_test_{int(time.time())}", "platform": "tiktok", "proxy": ""}, [200], "Thêm tài khoản mới"))
    test_cases.append(("POST", "/api/accounts/batch-import", {"raw_text": "acc_b1|p1\nacc_b2|p2", "platform": "tiktok"}, [200], "Nhập hàng loạt tài khoản"))
    test_cases.append(("POST", "/api/accounts/toggle-all?active=true", None, [200], "Bật tất cả tài khoản"))
    test_cases.append(("POST", "/api/accounts/nurture-batch", None, [200], "Nuôi hàng loạt tài khoản"))
    test_cases.append(("POST", "/api/accounts/stop-all", None, [200], "Dừng nuôi toàn bộ dàn kênh"))

    # 3. Proxies API
    test_cases.append(("GET", "/api/proxies", None, [200], "Lấy danh sách Proxy"))
    test_cases.append(("POST", "/api/proxies", {"proxy_str": f"192.168.1.{int(time.time()%250)}:8080", "location": "Việt Nam (VN)"}, [200], "Thêm Proxy Stealth"))
    test_cases.append(("POST", "/api/proxies/check-all", None, [200], "Kiểm tra toàn bộ Proxy"))

    # 4. Schedules API
    test_cases.append(("GET", "/api/schedules", None, [200], "Lấy lịch đăng tự động"))
    test_cases.append(("POST", "/api/schedules", {"platform": "tiktok", "time_slot": "11:30 (Trưa)", "account_id": 1}, [200], "Thêm lịch up video"))

    # 5. Logs API
    test_cases.append(("GET", "/api/logs?limit=50", None, [200], "Lấy nhật ký hệ thống"))
    test_cases.append(("POST", "/api/logs/clear", None, [200], "Làm sạch nhật ký"))

    # 6. Auth API
    test_cases.append(("POST", "/api/auth/login", {"username": "admin", "password": "123"}, [200], "Đăng nhập hệ thống"))
    test_cases.append(("POST", "/api/auth/register", {"username": f"user_{int(time.time())}", "password": "pass123", "role": "user", "full_name": "Nguyen Van Test"}, [200], "Đăng ký người dùng mới"))

    # 7. Growth & Audit Matrix
    test_cases.append(("POST", "/api/channel/growth-plan", {"channel_id": "@quetuduy", "product_name": "Phần mềm Auto AI"}, [200], "Ma trận 30 ngày xây kênh"))
    test_cases.append(("POST", "/api/channel/audit", {"channel_id": "@quetuduy"}, [200], "Chẩn đoán sức khỏe kênh AI"))
    test_cases.append(("POST", "/api/channel/target-nurture", {"channel_id": "@quetuduy"}, [200], "Nuôi kéo tệp kênh mục tiêu"))

    # 8. Stats & Niches
    test_cases.append(("GET", "/api/stats", None, [200], "Thống kê tổng quan hệ thống"))
    test_cases.append(("GET", "/api/niches", None, [200], "Danh mục ngành nghề tạo video"))
    test_cases.append(("GET", "/api/videos", None, [200], "Kho video đã xuất bản"))

    # 9. AI Video Generation
    test_cases.append(("POST", "/api/generate-video", {
        "industry": "Bán Lẻ & Thời Trang",
        "topic": "Cách phối đồ hack dáng",
        "product_name": "Áo thun local brand",
        "voice_gender": "nu"
    }, [200], "Tạo video AI 3 hồi (/api/generate-video)"))

    test_cases.append(("POST", "/api/ai-video/generate", {
        "niche": "cntt",
        "topic": "Vibe code trong 30 giây",
        "product_name": "Tool AI",
        "voice_gender": "nam"
    }, [200], "Tạo video AI Vue Dashboard (/api/ai-video/generate)"))

    passed = 0
    failed = 0

    for method, path, body, expected_statuses, label in test_cases:
        status, ok, data = request_api(method, path, body)
        is_pass = status in expected_statuses
        if is_pass:
            passed += 1
            icon = "✅ PASS"
        else:
            failed += 1
            icon = "❌ FAIL"

        print(f"[{icon}] {method:4} {path:35} -> HTTP {status:3} | {label}")
        if not is_pass:
            print(f"       Chi tiết lỗi: {data}")

    # 10. WebSocket Logs Test
    print("\n--- Kiểm tra kết nối WebSocket Live Server ---")
    try:
        import websockets
        import asyncio

        async def test_ws():
            async with websockets.connect("ws://127.0.0.1:8000/ws/logs", open_timeout=5) as ws:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                return msg

        ws_msg = asyncio.run(test_ws())
        passed += 1
        print(f"[✅ PASS] WS   ws://127.0.0.1:8000/ws/logs          -> Nhận phản hồi: {ws_msg[:50]}...")
    except Exception as e:
        failed += 1
        print(f"[❌ FAIL] WS   ws://127.0.0.1:8000/ws/logs          -> Lỗi kết nối: {e}")

    print("\n" + "=" * 70)
    print(f"  KẾT QUẢ TEST: {passed} PASS / {failed} FAIL")
    if failed == 0:
        print("  🎉 HỆ THỐNG 100% HOÀN HẢO - SẴN SÀNG SỬ DỤNG!")
    else:
        print("  ⚠️ VẪN CÒN LỖI CẦN XỬ LÝ!")
    print("=" * 70 + "\n")

    return failed == 0

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
