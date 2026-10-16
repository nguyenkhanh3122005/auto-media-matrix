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

            # Bảng quản lý Proxy Stealth
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS proxies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proxy_str TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'live',     -- 'live', 'die', 'checking'
                latency_ms INTEGER DEFAULT 45,
                ip_location TEXT DEFAULT 'Việt Nam (VN)',
                created_at TEXT NOT NULL
            )
            """)

            # Bảng Lịch Up Tự Động 24/7
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_id INTEGER,
                platform TEXT NOT NULL,
                time_slot TEXT NOT NULL,        -- '08:00', '11:30', '19:45'
                video_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
            )
            """)

            # Bảng Người Dùng & Phân Quyền (Admin / User)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',  -- 'admin' | 'user'
                full_name TEXT,
                created_at TEXT NOT NULL
            )
            """)

            # Seed tài khoản Admin & User mặc định nếu chưa có
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO users (username, password, role, full_name, created_at)
                    VALUES ('admin', 'admin123', 'admin', 'Quản Trị Viên Ngọc Khánh', ?),
                           ('ngockhanh', '123456', 'user', 'Ngọc Khánh Media User', ?)
                """, (now, now))

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

    # --- Proxy Management Methods ---
    def add_proxy(self, proxy_str: str, ip_location: str = "Việt Nam (VN)") -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT OR REPLACE INTO proxies (proxy_str, status, latency_ms, ip_location, created_at)
                VALUES (?, 'live', 48, ?, ?)
            """, (proxy_str.strip(), ip_location, now))
            conn.commit()
            return cursor.lastrowid

    def get_proxies(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM proxies ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_proxy(self, proxy_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM proxies WHERE id = ?", (proxy_id,))
            conn.commit()

    # --- Schedule Management Methods ---
    def add_schedule(self, platform: str, time_slot: str, account_id: Optional[int] = None) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO schedules (account_id, platform, time_slot, created_at)
                VALUES (?, ?, ?, ?)
            """, (account_id, platform.lower(), time_slot, now))
            conn.commit()
            return cursor.lastrowid

    def get_schedules(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM schedules ORDER BY id DESC")
            return [dict(row) for row in cursor.fetchall()]

    def delete_schedule(self, schedule_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
            conn.commit()

    def clear_logs(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM activity_logs")
            conn.commit()

    # --- Batch Import Accounts ---
    def batch_import_accounts(self, raw_text: str, default_platform: str = "tiktok") -> int:
        """
        Nhập hàng loạt tài khoản từ định dạng:
        Name|Platform|Proxy hoặc Username|Password|2FA|Proxy
        """
        lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
        imported_count = 0
        for line in lines:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                name = parts[0]
                platform = parts[1].lower() if parts[1].lower() in ['tiktok', 'facebook', 'youtube'] else default_platform
                proxy = parts[2] if len(parts) > 2 else ""
            else:
                name = parts[0]
                platform = default_platform
                proxy = ""

            qualified_name = f"({platform.upper()}): {name}"
            self.add_account(qualified_name, platform, method="browser", proxy=proxy)
            imported_count += 1

        self.add_log("Nhập hàng loạt tài khoản", "success", f"Đã nhập thành công {imported_count} kênh mới vào dàn")
        return imported_count

    # --- Authentication & User Management ---
    def register_user(self, username: str, password: str, role: str = "user", full_name: str = "") -> Optional[int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor.execute("""
                    INSERT INTO users (username, password, role, full_name, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (username.strip().lower(), password.strip(), role.lower(), full_name.strip() or username, now))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                return None

    def login_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, role, full_name, created_at 
                FROM users 
                WHERE username = ? AND password = ?
            """, (username.strip().lower(), password.strip()))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_users(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role, full_name, created_at FROM users ORDER BY id ASC")
            return [dict(row) for row in cursor.fetchall()]

db = Database()
