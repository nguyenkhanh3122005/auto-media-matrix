import os
import random
import time
import asyncio
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from config import PROFILES_DIR

# Danh sách User-Agents thực tế và hiện đại nhất (Windows 10/11)
COMMON_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

class BrowserManager:
    """Quản lý các phiên trình duyệt độc lập (Persistent Browser Contexts) cho từng tài khoản"""
    
    def __init__(self):
        self.active_contexts = {}

    def get_profile_path(self, profile_name: str) -> Path:
        sanitized = "".join(c for c in profile_name if c.isalnum() or c in ('_', '-'))
        path = PROFILES_DIR / sanitized
        path.mkdir(parents=True, exist_ok=True)
        return path

    def parse_proxy(self, proxy_str: str) -> Optional[Dict[str, str]]:
        """Phân tích proxy định dạng ip:port hoặc user:pass@ip:port hoặc http://..."""
        if not proxy_str or not proxy_str.strip():
            return None
        proxy_str = proxy_str.strip()
        if not proxy_str.startswith("http://") and not proxy_str.startswith("socks5://"):
            proxy_str = "http://" + proxy_str
            
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_str)
            proxy_dict = {"server": f"{parsed.scheme}://{parsed.hostname}:{parsed.port}"}
            if parsed.username:
                proxy_dict["username"] = parsed.username
            if parsed.password:
                proxy_dict["password"] = parsed.password
            return proxy_dict
        except Exception:
            return None

    def calculate_grid_bounds(self, index: int, total: int, screen_w: int = 1920, screen_h: int = 1040) -> Tuple[int, int, int, int]:
        """Tính toán kích thước và tọa độ cửa sổ để tự động xếp lưới (Auto-Tiling Grid)"""
        if total <= 1:
            return 0, 0, 1280, 800
        elif total <= 2:
            w = screen_w // 2
            h = screen_h
            return index * w, 0, w, h
        elif total <= 4:
            w = screen_w // 2
            h = screen_h // 2
            col = index % 2
            row = index // 2
            return col * w, row * h, w, h
        elif total <= 6:
            w = screen_w // 3
            h = screen_h // 2
            col = index % 3
            row = index // 3
            return col * w, row * h, w, h
        else:
            w = screen_w // 3
            h = screen_h // 3
            col = index % 3
            row = (index // 3) % 3
            return col * w, row * h, w, h

    async def launch_account_browser(self, account: Dict[str, Any], headless: bool = False, grid_pos: Optional[Tuple[int, int, int, int]] = None):
        """Khởi chạy trình duyệt Playwright với đầy đủ các thủ thuật chống phát hiện (Anti-bot)"""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise RuntimeError("Chưa cài đặt thư viện Playwright. Hãy chạy: pip install playwright && playwright install chromium")

        profile_path = self.get_profile_path(account.get("profile_id") or account.get("name"))
        proxy_config = self.parse_proxy(account.get("proxy", ""))
        user_agent = random.choice(COMMON_USER_AGENTS)

        playwright = await async_playwright().start()

        # Flags tối ưu hóa và bypass phát hiện bot của Chromium
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-site-isolation-trials",
            "--no-first-run",
            "--no-default-browser-check",
            "--ignore-certificate-errors",
            "--disable-web-security",
        ]

        viewport = {"width": 1280, "height": 800}
        if grid_pos:
            gx, gy, gw, gh = grid_pos
            args.append(f"--window-position={gx},{gy}")
            args.append(f"--window-size={gw},{gh}")
            viewport = {"width": gw - 20, "height": gh - 80}

        # Khởi chạy Persistent Context lưu lại phiên đăng nhập, cookie, cache vĩnh viễn
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            proxy=proxy_config,
            user_agent=user_agent,
            viewport=viewport,
            args=args,
            bypass_csp=True,
            java_script_enabled=True,
        )

        # Inject mã script xóa cờ bot navigator.webdriver
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['vi-VN', 'vi', 'en-US', 'en']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
        """)

        page = context.pages[0] if context.pages else await context.new_page()
        return playwright, context, page

    async def open_login_session(self, account: Dict[str, Any]):
        """Mở cửa sổ trình duyệt cho người dùng đăng nhập tài khoản thủ công (Lưu phiên vĩnh viễn)"""
        playwright, context, page = await self.launch_account_browser(account, headless=False)
        platform = account.get("platform", "tiktok").lower()
        
        target_url = "https://www.tiktok.com/login"
        if platform == "facebook":
            target_url = "https://www.facebook.com"
        elif platform == "youtube":
            target_url = "https://accounts.google.com"

        await page.goto(target_url)
        # Giữ phiên mở để người dùng đăng nhập
        return playwright, context, page

    @staticmethod
    async def human_delay(min_sec: float = 1.5, max_sec: float = 4.0):
        wait_time = random.uniform(min_sec, max_sec)
        await asyncio.sleep(wait_time)

    @staticmethod
    async def human_scroll(page, scroll_times: int = 3):
        for _ in range(scroll_times):
            scroll_step = random.randint(350, 750)
            await page.evaluate(f"window.scrollBy({{top: {scroll_step}, behavior: 'smooth'}});")
            await asyncio.sleep(random.uniform(1.2, 3.2))

    @staticmethod
    async def human_type(page, selector: str, text: str):
        for char in text:
            await page.type(selector, char, delay=random.randint(60, 180))
            if random.random() < 0.05:
                await asyncio.sleep(random.uniform(0.2, 0.5))

browser_manager = BrowserManager()
