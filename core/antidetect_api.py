import requests
import json
from typing import Optional, Dict, Any, Tuple
from config import ADSPOWER_API_URL, GOLOGIN_API_URL, HIDEMYACC_API_URL

class AntidetectManager:
    """Kết nối và điều khiển tự động qua API của AdsPower, GoLogin, Hidemyacc"""

    def __init__(self):
        pass

    def start_adspower_profile(self, profile_id: str) -> Optional[str]:
        """Gọi API AdsPower mở profile và lấy WebSocket CDP URL"""
        try:
            url = f"{ADSPOWER_API_URL}/api/v1/browser/start?user_id={profile_id}"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            if data.get("code") == 0:
                ws_endpoint = data.get("data", {}).get("ws", {}).get("puppeteer")
                return ws_endpoint
            else:
                print(f"[AdsPower] Lỗi mở profile {profile_id}: {data.get('msg')}")
                return None
        except Exception as e:
            print(f"[AdsPower] Không thể kết nối tới AdsPower Local API: {e}")
            return None

    def stop_adspower_profile(self, profile_id: str) -> bool:
        """Đóng profile AdsPower"""
        try:
            url = f"{ADSPOWER_API_URL}/api/v1/browser/stop?user_id={profile_id}"
            resp = requests.get(url, timeout=10)
            return resp.json().get("code") == 0
        except Exception:
            return False

    def start_hidemyacc_profile(self, profile_id: str) -> Optional[str]:
        """Gọi API Hidemyacc để mở profile"""
        try:
            url = f"{HIDEMYACC_API_URL}/api/v1/profiles/start/{profile_id}"
            resp = requests.get(url, timeout=15)
            data = resp.json()
            return data.get("wsUrl") or data.get("data", {}).get("ws")
        except Exception as e:
            print(f"[Hidemyacc] Không thể kết nối tới Hidemyacc API: {e}")
            return None

    def start_gologin_profile(self, profile_id: str) -> Optional[str]:
        """Gọi API GoLogin Local để mở profile"""
        try:
            url = f"{GOLOGIN_API_URL}/browser/start-profile"
            resp = requests.post(url, json={"profileId": profile_id}, timeout=15)
            data = resp.json()
            return data.get("wsUrl")
        except Exception as e:
            print(f"[GoLogin] Không thể kết nối tới GoLogin API: {e}")
            return None

    async def connect_cdp(self, ws_endpoint: str):
        """Kết nối Playwright vào Antidetect Browser qua Chrome DevTools Protocol (CDP)"""
        from playwright.async_api import async_playwright
        playwright = await async_playwright().start()
        browser = await playwright.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = context.pages[0] if context.pages else await context.new_page()
        return playwright, browser, context, page

antidetect_manager = AntidetectManager()
