import os
import subprocess
import hashlib
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

def get_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

class VideoRenderer:
    """Động cơ render video ngắn 9:16 (TikTok/Reels/Shorts) tự động bằng FFmpeg"""

    def __init__(self):
        self.output_dir = Path(__file__).resolve().parent.parent / "storage" / "generated_videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ffmpeg_exe = get_ffmpeg_exe()

    def get_file_md5(self, file_path: str) -> str:
        h = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    def spoof_video_metadata(self, file_path: str) -> str:
        """Lách thuật toán quét reup: Đổi mã MD5 bằng container padding và thay đổi nhẹ metadata"""
        try:
            with open(file_path, "ab") as f:
                # Ghi thêm chuỗi watermark vô hình không ảnh hưởng codec
                noise = f"//NGOCKHANH_MEDIA_SPOOF_{uuid.uuid4().hex}//".encode("utf-8")
                f.write(noise)
        except Exception as e:
            print(f"[!] Lỗi khi spoof MD5: {e}")
        return self.get_file_md5(file_path)

    def render_production_video(
        self,
        script_data: Dict[str, Any],
        voice_audio_path: str,
        output_filename: Optional[str] = None,
        width: int = 720,
        height: int = 1280
    ) -> Dict[str, Any]:
        """Dựng video MP4 chuẩn tỉ lệ dọc 9:16 ghép audio Edge-TTS, lồng nhạc nền và hiệu ứng chữ"""
        if not output_filename:
            output_filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

        output_path = str(self.output_dir / output_filename)
        topic = script_data.get("topic", "Khám phá bí kíp công nghệ 2026")
        niche_name = script_data.get("niche_name", "Xu Hướng Media")
        product = script_data.get("product_name", "")
        hook = script_data.get("hook", "")

        # Làm sạch ký tự đặc biệt cho FFmpeg filter
        clean_topic = topic.replace("'", "").replace(":", " - ").replace('"', '')
        clean_niche = niche_name.split('&')[0].strip().replace("'", "")
        clean_hook = hook.replace("'", "").replace(":", " - ").replace('"', '')

        # Tạo video nền chuyển động nhẹ kết hợp audio tiếng Việt
        # Filter:
        # 1. Nền gradient dark modern cyberpunk
        # 2. Hiệu ứng sóng âm waveform / nhấp nháy
        # 3. Text giật tít Hook & Title
        # 4. Mix nhạc nền BGM ngầm ở 15% âm lượng
        base_dir = Path(__file__).resolve().parent.parent
        code_video = str(base_dir / "assets" / "code_typing.mp4")
        app_img = str(base_dir / "assets" / "app_dashboard.png")

        if os.path.exists(code_video) and os.path.exists(app_img):
            cmd = [
                self.ffmpeg_exe, "-y",
                "-stream_loop", "-1", "-i", code_video,
                "-loop", "1", "-i", app_img,
                "-i", voice_audio_path,
                "-filter_complex", (
                    f"[0:v]trim=duration=5,scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setpts=PTS-STARTPTS[v0];"
                    f"[1:v]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},zoompan=z='min(zoom+0.0015,1.15)':d=900:s={width}x{height}:fps=25,setpts=PTS-STARTPTS[v1];"
                    f"[v0][v1]concat=n=2:v=1:a=0[v_base];"
                    f"[v_base]drawbox=x=0:y=0:w={width}:h=120:color=0x0f172a@0.9:t=fill,"
                    f"drawtext=text='⚡ NGOC KHANH MEDIA | {clean_niche}':fontcolor=0x00f0ff:fontsize=22:x=(w-text_w)/2:y=30,"
                    f"drawtext=text='{clean_topic[:36]}':fontcolor=white:fontsize=32:x=(w-text_w)/2:y=75[vout]"
                ),
                "-map", "[vout]",
                "-map", "2:a",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                output_path
            ]
        else:
            cmd = [
                self.ffmpeg_exe, "-y",
                "-f", "lavfi", "-i", f"color=c=0x0c101c:s={width}x{height}:r=25",
                "-i", voice_audio_path,
                "-filter_complex",
                (
                    f"[0:v]drawbox=x=0:y=0:w={width}:h=120:color=0x1e293b@0.8:t=fill,"
                    f"drawtext=text='⚡ NGOC KHANH MEDIA | {clean_niche}':fontcolor=0x00f0ff:fontsize=24:x=(w-text_w)/2:y=45,"
                    f"drawbox=x=40:y=180:w={width-80}:h=240:color=0x0284c7@0.2:t=fill,"
                    f"drawtext=text='{clean_topic[:36]}':fontcolor=white:fontsize=36:x=(w-text_w)/2:y=240[vout]"
                ),
                "-map", "[vout]",
                "-map", "1:a",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "128k",
                "-shortest",
                output_path
            ]

        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
            if process.returncode != 0:
                # Nếu filter drawtext gặp lỗi thiếu font trên Windows, chạy fallback đơn giản hơn
                cmd_simple = [
                    self.ffmpeg_exe, "-y",
                    "-f", "lavfi", "-i", f"color=c=0x0a1128:s={width}x{height}:r=25",
                    "-i", voice_audio_path,
                    "-c:v", "libx264",
                    "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-shortest",
                    output_path
                ]
                subprocess.run(cmd_simple, check=True, timeout=30)
        except Exception as e:
            print(f"[!] Lỗi khi render FFmpeg: {e}")
            # Fallback tạo file video tối thiểu
            cmd_fallback = [
                self.ffmpeg_exe, "-y",
                "-f", "lavfi", "-i", f"color=c=0x0a1128:s={width}x{height}:r=25",
                "-i", voice_audio_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                output_path
            ]
            subprocess.run(cmd_fallback, check=True, timeout=30)

        # Lách mã băm MD5 tự động (Video Spoofer)
        final_md5 = self.spoof_video_metadata(output_path)
        file_size_bytes = os.path.getsize(output_path)
        file_size_mb = f"{file_size_bytes / (1024 * 1024):.2f} MB"

        return {
            "status": "success",
            "video_path": output_path,
            "filename": output_filename,
            "video_url": f"/storage/generated_videos/{output_filename}",
            "file_size": file_size_mb,
            "md5_hash": final_md5,
            "aspect_ratio": "9:16 (Vertical)",
            "resolution": f"{width}x{height}"
        }

video_renderer = VideoRenderer()
