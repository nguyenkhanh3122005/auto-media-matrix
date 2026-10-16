import asyncio
import threading
import time
from typing import List, Dict, Any, Callable
from database.db import db
from engines.tiktok_engine import tiktok_engine
from engines.facebook_engine import facebook_engine
from engines.youtube_engine import youtube_engine
from core.video_processor import video_processor

class TaskRunner:
    """Điều phối và thực thi các tác vụ nuôi tài khoản và đăng video chạy ngầm đa luồng"""

    def __init__(self):
        self.is_running = False
        self.log_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self._loop = None
        self._thread = None

    def register_log_listener(self, callback: Callable[[Dict[str, Any]], None]):
        self.log_listeners.append(callback)

    def broadcast_log(self, log_entry: Dict[str, Any]):
        for listener in self.log_listeners:
            try:
                listener(log_entry)
            except Exception:
                pass

    async def execute_nurture(self, account_id: int, actions_count: int = 15):
        """Thực thi nuôi 1 tài khoản cụ thể"""
        account = db.get_account_by_id(account_id)
        if not account:
            return

        platform = account["platform"].lower()
        if platform == "tiktok":
            await tiktok_engine.nurture_account(account, actions_count)
        elif platform == "facebook":
            await facebook_engine.nurture_account(account, actions_count)
        elif platform == "youtube":
            await youtube_engine.nurture_account(account, actions_count)
        else:
            db.add_log("Nền tảng không hỗ trợ", "warning", f"Nền tảng {platform} chưa được cấu hình", account["name"], platform)

    async def execute_upload_queue(self):
        """Xử lý hàng đợi video chờ đăng"""
        pending_videos = db.get_videos(status="pending")
        if not pending_videos:
            return

        for video in pending_videos:
            account = db.get_account_by_id(video["account_id"]) if video["account_id"] else None
            if not account:
                # Tìm tài khoản phù hợp với platform của video
                accounts = db.get_accounts(platform=video["platform"])
                if accounts:
                    account = accounts[0]
                else:
                    db.add_log("Không có tài khoản đăng", "warning", f"Không tìm thấy tài khoản {video['platform']} nào để đăng video '{video['title']}'", "System", video["platform"])
                    continue

            # Bước 1: Xử lý đổi MD5 / lách bản quyền video trước khi tải lên
            db.add_log("Xử lý mã băm MD5", "info", f"Bắt đầu lách bản quyền cho video '{video['title']}'", account["name"], video["platform"])
            processed_file = video_processor.process_bypass_reup(video["file_path"])
            db.update_video_status(video["id"], "processing", processed_path=processed_file)

            # Bước 2: Tải video lên nền tảng
            platform = video["platform"].lower()
            if platform == "tiktok":
                await tiktok_engine.upload_video(account, video)
            elif platform == "facebook":
                await facebook_engine.upload_video(account, video)
            elif platform == "youtube":
                await youtube_engine.upload_video(account, video)

            # Giãn cách an toàn giữa các lần đăng video
            await asyncio.sleep(15)

    async def run_nurture_all(self, actions_per_account: int = 10):
        """Chạy nuôi tuần tự tất cả các tài khoản đang hoạt động"""
        accounts = db.get_accounts()
        for account in accounts:
            if account["status"] != "running":
                await self.execute_nurture(account["id"], actions_per_account)
                await asyncio.sleep(5)

    def start_background_nurture(self, account_id: Optional[int] = None, actions: int = 15):
        """Chạy nuôi trong background thread riêng biệt để không chặn Web/GUI"""
        def worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            if account_id:
                loop.run_until_complete(self.execute_nurture(account_id, actions))
            else:
                loop.run_until_complete(self.run_nurture_all(actions))
            loop.close()

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t

    def start_background_upload(self):
        """Chạy xử lý hàng đợi video trong background thread"""
        def worker():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.execute_upload_queue())
            loop.close()

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        return t

task_runner = TaskRunner()
