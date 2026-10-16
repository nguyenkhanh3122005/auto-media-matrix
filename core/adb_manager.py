import os
import subprocess
import time
import random
from typing import List, Optional, Dict
from config import POSSIBLE_ADB_PATHS

class ADBManager:
    """Điều khiển tự động hóa điện thoại thật hoặc giả lập Android (LDPlayer/Nox) qua ADB"""

    def __init__(self, custom_adb_path: Optional[str] = None):
        self.adb_bin = self._find_adb(custom_adb_path)

    def _find_adb(self, custom_path: Optional[str] = None) -> str:
        if custom_path and os.path.exists(custom_path):
            return custom_path

        for path in POSSIBLE_ADB_PATHS:
            if os.path.exists(path):
                return path

        # Thử gọi lệnh adb hệ thống
        try:
            res = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                return "adb"
        except Exception:
            pass

        return "adb" # Default fallback

    def is_available(self) -> bool:
        try:
            res = subprocess.run([self.adb_bin, "version"], capture_output=True, text=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def get_devices(self) -> List[str]:
        """Liệt kê danh sách các thiết bị/giả lập đang kết nối"""
        if not self.is_available():
            return []
        try:
            output = subprocess.check_output([self.adb_bin, "devices"]).decode("utf-8")
            lines = output.strip().split("\n")[1:]
            devices = []
            for line in lines:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
            return devices
        except Exception:
            return []

    def run_cmd(self, device: str, cmd_args: List[str]) -> str:
        full_cmd = [self.adb_bin, "-s", device] + cmd_args
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        return res.stdout

    def tap(self, device: str, x: int, y: int):
        # Thêm độ lệch ngẫu nhiên nhỏ để giống tay người thật chạm
        dx = x + random.randint(-5, 5)
        dy = y + random.randint(-5, 5)
        self.run_cmd(device, ["shell", "input", "tap", str(dx), str(dy)])

    def swipe(self, device: str, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 400):
        # Vuốt màn hình mô phỏng ngón tay
        self.run_cmd(device, ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration_ms)])

    def scroll_next_video(self, device: str):
        """Vuốt xem video tiếp theo (Shorts/TikTok/Reels)"""
        # Màn hình chuẩn 1080x1920 hoặc 720x1280
        start_y = random.randint(1300, 1500)
        end_y = random.randint(300, 450)
        x = random.randint(450, 600)
        duration = random.randint(320, 520)
        self.swipe(device, x, start_y, x, end_y, duration)

    def double_tap_like(self, device: str):
        """Chạm 2 lần vào giữa màn hình để thả tim video"""
        x = random.randint(480, 550)
        y = random.randint(900, 1050)
        self.tap(device, x, y)
        time.sleep(random.uniform(0.08, 0.15))
        self.tap(device, x, y)

    def push_video_to_gallery(self, device: str, local_video_path: str, remote_filename: str = "video_upload.mp4") -> bool:
        """Đẩy video từ máy tính vào thư viện ảnh/video của điện thoại/giả lập"""
        try:
            remote_path = f"/sdcard/DCIM/Camera/{remote_filename}"
            subprocess.run([self.adb_bin, "-s", device, "push", local_video_path, remote_path], check=True, timeout=60)
            # Quét lại MediaScanner để video lập tức xuất hiện trong thư viện ảnh
            self.run_cmd(device, ["shell", "am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{remote_path}"])
            return True
        except Exception as e:
            print(f"[ADB] Lỗi push video: {e}")
            return False

adb_manager = ADBManager()
