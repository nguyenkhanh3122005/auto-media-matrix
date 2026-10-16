import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import DB_PATH

class Database:
    def __init__(self, db_file=DB_PATH):
        self.db_file = str(db_file)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Bảng quản lý tài khoản (TikTok / Facebook / YouTube)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                platform TEXT NOT NULL,         -- 'tiktok', 'facebook', 'youtube'
                method TEXT NOT NULL,           -- 'browser', 'antidetect', 'adb'
                profile_id TEXT,                -- Tên thư mục profile hoặc ID antidetect / ID thiết bị ADB
                proxy TEXT,                     -- 'http://user:pass@ip:port' hoặc rỗng
                niche TEXT DEFAULT 'general',   -- Chủ đề (giải trí, kiếm tiền, làm đẹp, công nghệ...)
                status TEXT DEFAULT 'idle',     -- 'idle', 'running', 'error', 'checkpoint'
                last_run TEXT,
                actions_count INTEGER DEFAULT 0,
                is_enabled INTEGER DEFAULT 1,   -- 1: Bật nuôi, 0: Tắt nuôi
                followers_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """)

            # Tự động thêm cột nếu database cũ chưa có
            try:
                cursor.execute("ALTER TABLE accounts ADD COLUMN is_enabled INTEGER DEFAULT 1")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE accounts ADD COLUMN followers_count INTEGER DEFAULT 0")
            except Exception:
                pass

            # Bảng hàng đợi video cần đăng
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                file_path TEXT NOT NULL,
                processed_path TEXT,
                platform TEXT NOT NULL,
                account_id INTEGER,
                caption TEXT,
                hashtags TEXT,
                status TEXT DEFAULT 'pending',   -- 'pending', 'processing', 'scheduled', 'uploaded', 'failed'
                schedule_time TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL
            )
            """)

            # Bảng nhật ký hoạt động (Live Logs)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                account_name TEXT,
                platform TEXT,
                action TEXT NOT NULL,           -- 'scroll', 'like', 'comment', 'upload', 'error'
                status TEXT NOT NULL,           -- 'success', 'warning', 'error', 'info'
                details TEXT
            )
            """)

            # Bảng cài đặt chung (Key-Value)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """)
            conn.commit()

    # --- Account Methods ---
    def add_account(self, name: str, platform: str, method: str = "browser", profile_id: str = "", proxy: str = "", niche: str = "general") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT OR REPLACE INTO accounts (name, platform, method, profile_id, proxy, niche, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, platform.lower(), method.lower(), profile_id or name, proxy, niche, now))
            conn.commit()
            return cursor.lastrowid

    def get_accounts(self, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if platform:
                cursor.execute("SELECT * FROM accounts WHERE platform = ? ORDER BY id DESC", (platform.lower(),))
            else:
                cursor.execute("SELECT * FROM accounts ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_account_by_id(self, account_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE id = ?", (account_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_account_status(self, account_id: int, status: str, last_run: Optional[str] = None, increment_actions: bool = False):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if increment_actions:
                cursor.execute("UPDATE accounts SET status = ?, actions_count = actions_count + 1 WHERE id = ?", (status, account_id))
            else:
                cursor.execute("UPDATE accounts SET status = ? WHERE id = ?", (status, account_id))
            if last_run:
                cursor.execute("UPDATE accounts SET last_run = ? WHERE id = ?", (last_run, account_id))
            conn.commit()

    def toggle_account_enabled(self, account_id: int, is_enabled: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            val = 1 if is_enabled else 0
            cursor.execute("UPDATE accounts SET is_enabled = ? WHERE id = ?", (val, account_id))
            conn.commit()

    def toggle_all_accounts(self, is_enabled: bool):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            val = 1 if is_enabled else 0
            cursor.execute("UPDATE accounts SET is_enabled = ?", (val,))
            conn.commit()

    def delete_account(self, account_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE id = ?", (account_id,))
            conn.commit()

    # --- Video Queue Methods ---
    def add_video(self, title: str, file_path: str, platform: str, account_id: Optional[int] = None, 
                  caption: str = "", hashtags: str = "", schedule_time: Optional[str] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO videos (title, file_path, platform, account_id, caption, hashtags, schedule_time, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, file_path, platform.lower(), account_id, caption, hashtags, schedule_time, now))
            conn.commit()
            return cursor.lastrowid

    def get_videos(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT v.*, a.name as account_name 
                    FROM videos v LEFT JOIN accounts a ON v.account_id = a.id 
                    WHERE v.status = ? ORDER BY v.id DESC
                """, (status,))
            else:
                cursor.execute("""
                    SELECT v.*, a.name as account_name 
                    FROM videos v LEFT JOIN accounts a ON v.account_id = a.id 
                    ORDER BY v.id DESC
                """)
            return [dict(row) for row in cursor.fetchall()]

    def update_video_status(self, video_id: int, status: str, processed_path: Optional[str] = None, error_message: Optional[str] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            params = [status]
            sql = "UPDATE videos SET status = ?"
            if processed_path:
                sql += ", processed_path = ?"
                params.append(processed_path)
            if error_message:
                sql += ", error_message = ?"
                params.append(error_message)
            sql += " WHERE id = ?"
            params.append(video_id)
            cursor.execute(sql, tuple(params))
            conn.commit()

    # --- Activity Logs ---
    def add_log(self, action: str, status: str = "info", details: str = "", account_name: str = "System", platform: str = "ALL"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO activity_logs (timestamp, account_name, platform, action, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (now, account_name, platform, action, status, details))
            conn.commit()

    def get_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM activity_logs ORDER BY id DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- System Stats ---
    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM accounts")
            total_accounts = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 'running'")
            running_accounts = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM videos")
            total_videos = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM videos WHERE status = 'uploaded'")
            uploaded_videos = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(actions_count) FROM accounts")
            total_actions = cursor.fetchone()[0] or 0

            return {
                "total_accounts": total_accounts,
                "running_accounts": running_accounts,
                "total_videos": total_videos,
                "uploaded_videos": uploaded_videos,
                "total_actions": total_actions
            }

db = Database()
