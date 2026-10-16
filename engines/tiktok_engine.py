import asyncio
import random
import time
from typing import Dict, Any, Optional
from core.browser_manager import browser_manager
from core.antidetect_api import antidetect_manager
from core.adb_manager import adb_manager
from config import DEFAULT_NURTURE_CONFIG, COMMENT_TEMPLATES
from database.db import db

class TikTokEngine:
    """Động cơ tự động nuôi tài khoản và đăng video TikTok"""

    async def nurture_account(self, account: Dict[str, Any], session_actions: int = 15):
        """Kịch bản nuôi nick TikTok: Lướt For You Page, xem video đủ thời lượng, like, comment ngẫu nhiên"""
        account_name = account["name"]
        method = account.get("method", "browser")
        db.add_log("Bắt đầu nuôi nick TikTok", "info", f"Phương pháp: {method}, mục tiêu: {session_actions} video", account_name, "TikTok")
        db.update_account_status(account["id"], "running")

        if method == "adb":
            # Nuôi qua thiết bị Android / Giả lập LDPlayer
            device = account.get("profile_id") or (adb_manager.get_devices()[0] if adb_manager.get_devices() else None)
            if not device:
                err_msg = "Không tìm thấy thiết bị ADB / Giả lập kết nối."
                db.add_log("Lỗi ADB", "error", err_msg, account_name, "TikTok")
                db.update_account_status(account["id"], "error")
                return False

            db.add_log("Khởi động TikTok ADB", "info", f"Thiết bị: {device}", account_name, "TikTok")
            # Mở ứng dụng TikTok
            adb_manager.run_cmd(device, ["shell", "monkey", "-p", "com.zhiliaoapp.musically", "-c", "android.intent.category.LAUNCHER", "1"])
            await asyncio.sleep(6)

            for i in range(session_actions):
                # Xem video từ 10 - 30 giây ngẫu nhiên
                watch_time = random.uniform(DEFAULT_NURTURE_CONFIG["min_watch_seconds"], DEFAULT_NURTURE_CONFIG["max_watch_seconds"])
                await asyncio.sleep(watch_time)

                # Xác suất thả tim
                if random.random() < DEFAULT_NURTURE_CONFIG["like_probability"]:
                    adb_manager.double_tap_like(device)
                    db.add_log("Tương tác TikTok ADB", "success", f"Đã thả tim video #{i+1}", account_name, "TikTok")

                # Vuốt sang video tiếp theo
                adb_manager.scroll_next_video(device)
                db.update_account_status(account["id"], "running", increment_actions=True)

            db.update_account_status(account["id"], "idle", last_run=time.strftime("%Y-%m-%d %H:%M:%S"))
            db.add_log("Hoàn thành phiên nuôi TikTok ADB", "success", f"Đã lướt xong {session_actions} video", account_name, "TikTok")
            return True

        # Nuôi qua Trình duyệt (Playwright độc lập hoặc Antidetect API)
        playwright = None
        context = None
        browser = None
        try:
            if method == "antidetect":
                ws_url = antidetect_manager.start_adspower_profile(account.get("profile_id"))
                if not ws_url:
                    ws_url = antidetect_manager.start_hidemyacc_profile(account.get("profile_id"))
                if not ws_url:
                    raise RuntimeError("Không thể kết nối Antidetect API. Vui lòng mở sẵn ứng dụng AdsPower/Hidemyacc.")
                playwright, browser, context, page = await antidetect_manager.connect_cdp(ws_url)
            else:
                playwright, context, page = await browser_manager.launch_account_browser(account, headless=False)

            # Truy cập TikTok FYP
            db.add_log("Mở trang TikTok", "info", "Đang truy cập https://www.tiktok.com/foryou", account_name, "TikTok")
            await page.goto("https://www.tiktok.com/foryou", wait_until="networkidle", timeout=45000)
            await asyncio.sleep(5)

            # Lướt và tương tác
            for i in range(session_actions):
                watch_time = random.uniform(DEFAULT_NURTURE_CONFIG["min_watch_seconds"], DEFAULT_NURTURE_CONFIG["max_watch_seconds"])
                db.add_log("Đang xem video", "info", f"Xem video #{i+1} trong {int(watch_time)}s", account_name, "TikTok")
                await asyncio.sleep(watch_time)

                # Xác suất thả tim
                if random.random() < DEFAULT_NURTURE_CONFIG["like_probability"]:
                    try:
                        like_buttons = await page.query_selector_all('button[aria-label*="Like"], span[data-e2e="like-icon"]')
                        if like_buttons:
                            await like_buttons[-1].click()
                            db.add_log("Thả tim TikTok", "success", f"Đã like video #{i+1}", account_name, "TikTok")
                    except Exception:
                        pass

                # Xác suất bình luận
                if random.random() < DEFAULT_NURTURE_CONFIG["comment_probability"]:
                    comment_text = random.choice(COMMENT_TEMPLATES)
                    try:
                        comment_box = await page.query_selector('div[contenteditable="true"], input[placeholder*="Add comment"]')
                        if comment_box:
                            await comment_box.click()
                            await browser_manager.human_type(page, 'div[contenteditable="true"]', comment_text)
                            await page.keyboard.press("Enter")
                            db.add_log("Bình luận TikTok", "success", f"Bình luận: '{comment_text}'", account_name, "TikTok")
                    except Exception:
                        pass

                # Nhấn phím mũi tên xuống (Down Arrow) để sang video tiếp theo
                await page.keyboard.press("ArrowDown")
                db.update_account_status(account["id"], "running", increment_actions=True)
                await browser_manager.human_delay(2, 5)

            db.update_account_status(account["id"], "idle", last_run=time.strftime("%Y-%m-%d %H:%M:%S"))
            db.add_log("Hoàn thành nuôi nick", "success", f"Đã nuôi thành công {session_actions} lượt xem", account_name, "TikTok")
            return True

        except Exception as e:
            db.add_log("Lỗi phiên nuôi TikTok", "error", str(e), account_name, "TikTok")
            db.update_account_status(account["id"], "error")
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

    async def upload_video(self, account: Dict[str, Any], video_item: Dict[str, Any]) -> bool:
        """Tự động tải video lên TikTok Creator Studio"""
        account_name = account["name"]
        video_id = video_item["id"]
        file_to_upload = video_item.get("processed_path") or video_item["file_path"]
        caption_full = f"{video_item.get('caption', '')} {video_item.get('hashtags', '')}".strip()

        db.add_log("Bắt đầu đăng video TikTok", "info", f"Tệp: {file_to_upload}", account_name, "TikTok")
        db.update_video_status(video_id, "processing")

        playwright = None
        context = None
        try:
            playwright, context, page = await browser_manager.launch_account_browser(account, headless=False)
            
            # Mở trang Upload TikTok
            await page.goto("https://www.tiktok.com/creator-center/upload?from=upload", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(6)

            # Tìm iframe hoặc input tải file
            upload_input = await page.wait_for_selector('input[type="file"]', timeout=30000)
            if not upload_input:
                # Kiểm tra bên trong iframe nếu TikTok nhúng iframe
                for frame in page.frames:
                    upload_input = await frame.query_selector('input[type="file"]')
                    if upload_input:
                        break

            if not upload_input:
                raise Exception("Không tìm thấy nút chọn file tải lên trên TikTok (Có thể bạn chưa đăng nhập tài khoản).")

            # Đẩy file video vào input
            await upload_input.set_input_files(file_to_upload)
            db.add_log("Tải tệp video", "info", "Đã chọn file video thành công, đang chờ xử lý", account_name, "TikTok")
            await asyncio.sleep(10)

            # Điền Caption & Hashtags
            caption_input = await page.query_selector('div[contenteditable="true"], .notranslate.public-DraftEditor-content')
            if caption_input:
                await caption_input.click()
                # Xóa caption mặc định nếu có
                await page.keyboard.press("Control+A")
                await page.keyboard.press("Backspace")
                await browser_manager.human_type(page, 'div[contenteditable="true"]', caption_full)
                db.add_log("Điền Caption", "info", f"Đã nhập caption và hashtags", account_name, "TikTok")

            await asyncio.sleep(5)

            # Tìm nút Đăng (Post)
            post_button = await page.query_selector('button:has-text("Post"), button:has-text("Đăng")')
            if post_button:
                await post_button.click()
                db.add_log("Bấm nút Đăng", "info", "Đã gửi lệnh đăng video...", account_name, "TikTok")
                await asyncio.sleep(10)

            db.update_video_status(video_id, "uploaded")
            db.add_log("Đăng video thành công", "success", f"Video '{video_item['title']}' đã được tải lên TikTok!", account_name, "TikTok")
            return True

        except Exception as e:
            err = str(e)
            db.add_log("Đăng video thất bại", "error", err, account_name, "TikTok")
            db.update_video_status(video_id, "failed", error_message=err)
            return False
        finally:
            if context:
                await context.close()
            if playwright:
                await playwright.stop()

tiktok_engine = TikTokEngine()
