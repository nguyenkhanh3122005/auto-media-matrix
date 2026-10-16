import urllib.request
import urllib.error
import json
import socket
import time
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, path, body=None):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
        data = json.dumps(body).encode("utf-8")
    else:
        data = None

    try:
        with urllib.request.urlopen(req, data=data, timeout=10) as response:
            status = response.status
            content = response.read().decode("utf-8", errors="replace")
            try:
                res_json = json.loads(content)
            except Exception:
                res_json = content[:100]
            return status, True, res_json
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8", errors="replace")
        return e.code, False, content
    except Exception as e:
        return 0, False, str(e)

endpoints = [
    ("GET", "/"),
    ("GET", "/favicon.ico"),
    ("GET", "/api/accounts"),
    ("GET", "/api/logs?limit=50"),
    ("GET", "/api/proxies"),
    ("GET", "/api/schedules"),
    ("GET", "/api/stats"),
    ("POST", "/api/auth/login", {"username": "admin", "password": "123"}),
    ("POST", "/api/auth/register", {"username": "test_user_99", "password": "password123", "role": "user", "full_name": "Test User"}),
    ("POST", "/api/channel/growth-plan", {"channel_id": "@quetuduy", "product_name": "AI Tool", "niche": "cntt"}),
    ("POST", "/api/channel/audit", {"channel_id": "@quetuduy"}),
    ("POST", "/api/channel/target-nurture", {"channel_id": "@quetuduy"}),
    ("POST", "/api/accounts/nurture-batch?duration_minutes=10", {}),
    ("POST", "/api/accounts/stop-all", {}),
    ("POST", "/api/accounts/toggle-all?active=true", {}),
    ("POST", "/api/accounts", {"name": "Test Acc", "platform": "tiktok", "proxy": ""}),
    ("POST", "/api/accounts/batch-import", {"raw_text": "acc1|pass|2fa", "platform": "tiktok"}),
    ("POST", "/api/proxies", {"proxy_str": "127.0.0.1:8080", "location": "VN"}),
    ("POST", "/api/proxies/check-all", {}),
    ("POST", "/api/schedules", {"platform": "tiktok", "time_slot": "11:30", "account_id": 1}),
    ("POST", "/api/logs/clear", {}),
    ("POST", "/api/ai-video/generate", {"niche": "cntt", "topic": "Vibe code", "product_name": "AI Tool", "voice_gender": "nu"}),
    ("POST", "/api/generate-video", {"industry": "CNTT", "topic": "Vibe code", "product_name": "AI Tool"}),
]

print("--- TESTING ALL SERVER 8000 ENDPOINTS ---")
results = []
for method, path, *extra in endpoints:
    body = extra[0] if extra else None
    status, ok, res = test_endpoint(method, path, body)
    symbol = "✅ PASS" if (ok or status in [200, 204]) else "❌ FAIL"
    print(f"[{symbol}] {method:4} {path:35} -> HTTP {status}")
    results.append((symbol, method, path, status, res))

passed = sum(1 for r in results if "PASS" in r[0])
failed = sum(1 for r in results if "FAIL" in r[0])
print(f"\nTOTAL: {passed} PASS / {failed} FAIL")
