import os
import shutil
import hashlib
import random
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from config import PROCESSED_VIDEOS_DIR

class VideoProcessor:
    """Xử lý video tự động: Thay đổi mã băm MD5, làm sạch metadata, lách bản quyền nhẹ"""

    def __init__(self, output_dir: Path = PROCESSED_VIDEOS_DIR):
        self.output_dir = output_dir

    def calculate_md5(self, file_path: str) -> str:
        """Tính mã băm MD5 của video"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def modify_md5_fast(self, input_path: str, output_path: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Thay đổi 100% mã băm MD5 tức thì (chỉ mất 0.01s) bằng kỹ thuật chèn binary padding
        vào cuối file MP4 mà không làm hỏng cấu trúc video hoặc giảm chất lượng.
        """
        in_p = Path(input_path)
        if not output_path:
            output_path = str(self.output_dir / f"mod_{random.randint(1000, 9999)}_{in_p.name}")

        old_md5 = self.calculate_md5(input_path)

        # Copy file sang vị trí mới
        shutil.copy2(input_path, output_path)

        # Chèn thêm một chuỗi byte ngẫu nhiên vào cuối file
        junk_bytes = os.urandom(random.randint(64, 256))
        with open(output_path, "ab") as f:
            f.write(junk_bytes)

        new_md5 = self.calculate_md5(output_path)
        return output_path, old_md5, new_md5

    def process_bypass_reup(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        Xử lý lách bản quyền nâng cao bằng FFmpeg (nếu có sẵn trên máy):
        - Thay đổi nhẹ tốc độ (1.02x)
        - Đổi pitch âm thanh
        - Zoom nhẹ 2%
        - Xóa sạch metadata Exif cũ
        Nếu không có FFmpeg, tự động chuyển về kỹ thuật Binary MD5 Modifier.
        """
        in_p = Path(input_path)
        if not output_path:
            output_path = str(self.output_dir / f"render_{random.randint(1000, 9999)}_{in_p.name}")

        # Kiểm tra xem ffmpeg có khả dụng không
        try:
            check = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=2)
            has_ffmpeg = (check.returncode == 0)
        except Exception:
            has_ffmpeg = False

        if not has_ffmpeg:
            # Fallback an toàn sang thay đổi MD5
            out_file, _, _ = self.modify_md5_fast(input_path, output_path)
            return out_file

        # Có FFmpeg: Áp dụng bộ lọc lách bản quyền video ngắn
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "scale=iw*1.02:ih*1.02,crop=iw/1.02:ih/1.02,eq=contrast=1.03:brightness=0.01",
            "-af", "atempo=1.02,asetrate=44100*1.01",
            "-map_metadata", "-1", # Xóa toàn bộ thông tin metadata nguồn
            "-c:v", "libx264", "-crf", "22", "-preset", "veryfast",
            "-c:a", "aac", "-b:a", "128k",
            output_path
        ]
        
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=180)
            return output_path
        except Exception:
            # Nếu render lỗi, fallback về fast MD5
            out_file, _, _ = self.modify_md5_fast(input_path, output_path)
            return out_file

video_processor = VideoProcessor()
