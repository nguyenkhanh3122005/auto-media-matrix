import asyncio
import random
import time
from typing import Dict, Any
from core.browser_manager import browser_manager
from core.antidetect_api import antidetect_manager
from core.adb_manager import adb_manager
from config import DEFAULT_NURTURE_CONFIG, COMMENT_TEMPLATES
from database.db import db

class FacebookEngine:
    """Động cơ nuôi tài khoản và đăng Reels Facebook tự động"""

    async def nurture_account(self, account: Dict[str, Any], session_actions: int = 15):
        """Nuôi nick Facebook: Lướt Reels, tương tác Like, lướt Newsfeed"""
        account_name = account["name"]
        method = account.get("method", "browser")
        db.add_log("Bắt đầu nuôi nick Facebook", "info", f"Phương pháp: {method}", account_name, "Facebook")
        db.update_account_status(account["id"], "running")

        if method == "adb":
            device = account.get("profile_id") or (adb_manager.get_devices()[0] if adb_manager.get_devices() else None)
            if not device:
                db.add_log("Lỗi ADB", "error", "Không tìm thấy thiết bị ADB", account_name, "Facebook")
                db.update_account_status(account["id"], "error")
                return False

            # Mở Facebook App
            adb_manager.run_cmd(device, ["shell", "monkey", "-p", "com.facebook.katana", "-c", "android.intent.category.LAUNCHER", "1"])
            await asyncio.sleep(6)

            for i in range(session_actions):
                watch_time = random.uniform(DEFAULT_NURTURE_CONFIG["min_watch_seconds"], DEFAULT_NURTURE_CONFIG["max_watch_seconds"])
                await asyncio.sleep(watch_time)

                if random.random() < DEFAULT_NURTURE_CONFIG["like_probability"]:
                    adb_manager.double_tap_like(device)
                    db.add_log("Tương tác FB Reels", "success", f"Đã like reels #{i+1}", account_name, "Facebook")

                adb_manager.scroll_next_video(device)
                db.update_account_status(account["id"], "running", increment_actions=True)

            db.update_account_status(account["id"], "idle", last_run=time.strftime("%Y-%m-%d %H:%M:%S"))
            db.add_log("Hoàn thành nuôi FB", "success", f"Đã lướt xong {session_actions} video", account_name, "Facebook")
            return True

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

            # Vào Facebook Reels
            db.add_log("Mở Facebook Reels", "info", "Đang mở https://www.facebook.com/reel", account_name, "Facebook")
            await page.goto("https://www.facebook.com/reel", wait_until="networkidle", timeout=45000)
            await asyncio.sleep(5)

            for i in range(session_actions):
                watch_time = random.uniform(DEFAULT_NURTURE_CONFIG["min_watch_seconds"], DEFAULT_NURTURE_CONFIG["max_watch_seconds"])
                db.add_log("Xem FB Reel", "info", f"Xem video #{i+1} trong {int(watch_time)}s", account_name, "Facebook")
                await asyncio.sleep(watch_time)

                # Like
                if random.random() < DEFAULT_NURTURE_CONFIG["like_probability"]:
                    try:
                        like_btn = await page.query_selector('div[aria-label="Thích"], div[aria-label="Like"]')
                        if like_btn:
                            await like_btn.click()
                            db.add_log("Thích Reels", "success", f"Đã like reels #{i+1}", account_name, "Facebook")
                    except Exception:
                        pass

                # Cuộn xem reels tiếp theo
                await page.keyboard.press("ArrowDown")
                db.update_account_status(account["id"], "running", increment_actions=True)
                await browser_manager.human_delay(2, 4)

            db.update_account_status(account["id"], "idle", last_run=time.strftime("%Y-%m-%d %H:%M:%S"))
            db.add_log("Hoàn thành phiên nuôi FB", "success", "Tài khoản đã hoạt động tự nhiên", account_name, "Facebook")
            return True

        except Exception as e:
            db.add_log("Lỗi nuôi FB", "error", str(e), account_name, "Facebook")
            db.update_account_status(account["id"], "error")
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

    async def upload_video(self, account: Dict[str, Any], video_item: Dict[str, Any]) -> bool:
        """Đăng Reels lên Facebook cá nhân hoặc Fanpage"""
        account_name = account["name"]
        video_id = video_item["id"]
        file_to_upload = video_item.get("processed_path") or video_item["file_path"]
        caption_full = f"{video_item.get('caption', '')} {video_item.get('hashtags', '')}".strip()

        db.add_log("Bắt đầu đăng FB Reels", "info", f"File: {file_to_upload}", account_name, "Facebook")
        db.update_video_status(video_id, "processing")

        playwright = None
        context = None
        try:
            playwright, context, page = await browser_manager.launch_account_browser(account, headless=False)
            await page.goto("https://www.facebook.com/reel/create", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(6)

            upload_input = await page.wait_for_selector('input[type="file"]', timeout=30000)
            if not upload_input:
                raise Exception("Không tìm thấy nút upload Reels. Vui lòng kiểm tra đăng nhập Facebook.")

            await upload_input.set_input_files(file_to_upload)
            db.add_log("Tải video lên FB", "info", "Đã chọn video, đang chờ tải", account_name, "Facebook")
            await asyncio.sleep(8)

            # Bấm Tiếp (Next)
            next_btn = await page.query_selector('div[aria-label="Tiếp"], div[aria-label="Next"]')
            if next_btn:
                await next_btn.click()
                await asyncio.sleep(3)
                next_btn2 = await page.query_selector('div[aria-label="Tiếp"], div[aria-label="Next"]')
                if next_btn2:
                    await next_btn2.click()
                    await asyncio.sleep(3)

            # Nhập Caption mô tả Reels
            caption_input = await page.query_selector('div[contenteditable="true"], div[aria-label*="Mô tả"], div[aria-label*="Describe"]')
            if caption_input:
                await caption_input.click()
                await browser_manager.human_type(page, 'div[contenteditable="true"]', caption_full)

            await asyncio.sleep(4)

            # Nút Đăng (Publish)
            post_btn = await page.query_selector('div[aria-label="Đăng"], div[aria-label="Publish"]')
            if post_btn:
                await post_btn.click()
                db.add_log("Gửi lệnh đăng Reels", "info", "Đã bấm Đăng Reels...", account_name, "Facebook")
                await asyncio.sleep(12)

            db.update_video_status(video_id, "uploaded")
            db.add_log("Đăng FB Reels thành công", "success", f"Đã đăng '{video_item['title']}' lên Facebook", account_name, "Facebook")
            return True

        except Exception as e:
            err = str(e)
            db.add_log("Lỗi đăng FB Reels", "error", err, account_name, "Facebook")
            db.update_video_status(video_id, "failed", error_message=err)
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

facebook_engine = FacebookEngine()
