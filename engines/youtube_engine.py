import asyncio
import random
import time
from typing import Dict, Any
from core.browser_manager import browser_manager
from core.antidetect_api import antidetect_manager
from config import DEFAULT_NURTURE_CONFIG
from database.db import db

class YouTubeEngine:
    """Động cơ nuôi tài khoản và đăng YouTube Shorts tự động"""

    async def nurture_account(self, account: Dict[str, Any], session_actions: int = 15):
        """Nuôi nick YouTube Shorts: Xem Shorts, like ngẫu nhiên, xem đề xuất"""
        account_name = account["name"]
        method = account.get("method", "browser")
        db.add_log("Bắt đầu nuôi nick YouTube", "info", f"Phương pháp: {method}", account_name, "YouTube")
        db.update_account_status(account["id"], "running")

        playwright = None
        context = None
        try:
            if method == "antidetect":
                ws_url = antidetect_manager.start_adspower_profile(account.get("profile_id"))
                if not ws_url:
                    ws_url = antidetect_manager.start_hidemyacc_profile(account.get("profile_id"))
                playwright, browser, context, page = await antidetect_manager.connect_cdp(ws_url)
            else:
                playwright, context, page = await browser_manager.launch_account_browser(account, headless=False)

            # Vào YouTube Shorts
            db.add_log("Mở YouTube Shorts", "info", "Đang mở https://www.youtube.com/shorts", account_name, "YouTube")
            await page.goto("https://www.youtube.com/shorts", wait_until="networkidle", timeout=45000)
            await asyncio.sleep(5)

            for i in range(session_actions):
                watch_time = random.uniform(DEFAULT_NURTURE_CONFIG["min_watch_seconds"], DEFAULT_NURTURE_CONFIG["max_watch_seconds"])
                db.add_log("Xem YouTube Short", "info", f"Xem video #{i+1} ({int(watch_time)}s)", account_name, "YouTube")
                await asyncio.sleep(watch_time)

                # Like
                if random.random() < DEFAULT_NURTURE_CONFIG["like_probability"]:
                    try:
                        like_btn = await page.query_selector('ytd-like-button-renderer button')
                        if like_btn:
                            await like_btn.click()
                            db.add_log("Thích Short", "success", f"Đã like shorts #{i+1}", account_name, "YouTube")
                    except Exception:
                        pass

                # Chuyển short tiếp theo
                await page.keyboard.press("ArrowDown")
                db.update_account_status(account["id"], "running", increment_actions=True)
                await browser_manager.human_delay(2, 4)

            db.update_account_status(account["id"], "idle", last_run=time.strftime("%Y-%m-%d %H:%M:%S"))
            db.add_log("Hoàn thành nuôi YouTube", "success", "Tài khoản YouTube đã được tương tác tự nhiên", account_name, "YouTube")
            return True

        except Exception as e:
            db.add_log("Lỗi nuôi YouTube", "error", str(e), account_name, "YouTube")
            db.update_account_status(account["id"], "error")
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

    async def upload_video(self, account: Dict[str, Any], video_item: Dict[str, Any]) -> bool:
        """Đăng Shorts lên YouTube Studio"""
        account_name = account["name"]
        video_id = video_item["id"]
        file_to_upload = video_item.get("processed_path") or video_item["file_path"]
        title_full = f"{video_item.get('title', '')} #Shorts"

        db.add_log("Bắt đầu đăng YouTube Shorts", "info", f"Tệp: {file_to_upload}", account_name, "YouTube")
        db.update_video_status(video_id, "processing")

        playwright = None
        context = None
        try:
            playwright, context, page = await browser_manager.launch_account_browser(account, headless=False)
            await page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(6)

            # Nút Create / Upload
            create_btn = await page.query_selector('#create-icon, ytcp-button#create-icon')
            if create_btn:
                await create_btn.click()
                await asyncio.sleep(1)
                upload_item = await page.query_selector('tp-yt-paper-item:has-text("Upload videos"), tp-yt-paper-item:has-text("Tải video lên")')
                if upload_item:
                    await upload_item.click()

            # Upload input
            upload_input = await page.wait_for_selector('input[type="file"]', timeout=30000)
            await upload_input.set_input_files(file_to_upload)
            db.add_log("Tải file lên YouTube", "info", "File đã được gửi lên YouTube Studio", account_name, "YouTube")
            await asyncio.sleep(10)

            # Chọn "Không dành cho trẻ em"
            not_kids_radio = await page.query_selector('tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"]')
            if not_kids_radio:
                await not_kids_radio.click()

            # Bấm Next 3 lần qua các bước
            for _ in range(3):
                next_btn = await page.query_selector('#next-button')
                if next_btn:
                    await next_btn.click()
                    await asyncio.sleep(2)

            # Chọn Công khai (Public)
            public_radio = await page.query_selector('tp-yt-paper-radio-button[name="PUBLIC"]')
            if public_radio:
                await public_radio.click()
                await asyncio.sleep(2)

            # Nút Xuất bản (Publish)
            done_btn = await page.query_selector('#done-button')
            if done_btn:
                await done_btn.click()
                db.add_log("Xuất bản YouTube Shorts", "info", "Đang lưu và công khai video...", account_name, "YouTube")
                await asyncio.sleep(8)

            db.update_video_status(video_id, "uploaded")
            db.add_log("Đăng Shorts thành công", "success", f"Đã đăng '{video_item['title']}' lên YouTube!", account_name, "YouTube")
            return True

        except Exception as e:
            err = str(e)
            db.add_log("Lỗi đăng YouTube Shorts", "error", err, account_name, "YouTube")
            db.update_video_status(video_id, "failed", error_message=err)
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

youtube_engine = YouTubeEngine()
