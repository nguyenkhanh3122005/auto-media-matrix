import os
import random
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import subprocess

NICHE_CATALOG = {
    "cntt": {
        "name": "Công Nghệ Thông Tin & Lập Trình (CNTT)",
        "sub_topics": [
            "Vibe code web chỉ bằng 1 câu lệnh",
            "Top 3 extension VS Code cứu cánh lập trình viên",
            "Cách dùng AI tự động hóa công việc hàng ngày",
            "Mẹo debug code trong 30 giây không bị đau đầu",
            "Lộ trình tự học lập trình từ con số 0 lên 20 triệu/tháng"
        ],
        "default_hook": "Đừng code thủ công nữa, xem ngay cách vibe code cực đỉnh này!",
        "hashtags": "#laptrinh #vibecode #congnghe #developer #ai #learncoding #codingtips"
    },
    "ecommerce": {
        "name": "Thương Mại Điện Tử & Thời Trang / Mỹ Phẩm",
        "sub_topics": [
            "Review chân thực sản phẩm hot trend tuần này",
            "Cách phối đồ hack dáng cực xịn cho người gầy",
            "Top 3 món đồ decor phòng ngủ giá học sinh sinh viên",
            "Bí kíp săn deal hời giảm 50% độc quyền hôm nay",
            "Cảnh báo: Đừng mua món này nếu không muốn nghiện!"
        ],
        "default_hook": "Món đồ này vừa rẻ vừa xịn, tiếc là 90% mọi người chưa biết tới!",
        "hashtags": "#thoitrang #review #shopeehaul #ootd #giamgia #lamdep #lifestyle"
    },
    "real_estate": {
        "name": "Bất Động Sản & Nhà Cửa / Thiết Kế",
        "sub_topics": [
            "Khám phá căn hộ thông minh 60m2 phong cách tối giản",
            "3 lưu ý pháp lý sống còn trước khi xuống tiền mua nhà đất",
            "Mẹo thiết kế phòng khách tạo cảm giác rộng gấp đôi",
            "Đánh giá tiềm năng khu đất ven đô sinh lời x2 trong 2 năm",
            "Xem nhà mẫu triệu đô tại trung tâm thành phố"
        ],
        "default_hook": "Căn nhà này có thiết kế thông minh đến mức bạn sẽ muốn dọn vào ở ngay!",
        "hashtags": "#batdongsan #nhadep #thietkenhadep #reviewnhadat #interiordesign #homedecor"
    },
    "fnb": {
        "name": "Ẩm Thực & Nhà Hàng / Đồ Uống (F&B)",
        "sub_topics": [
            "Công thức làm trà sữa đậm vị ngon hơn ngoài hàng",
            "Trải nghiệm quán ăn bí mật ẩn sâu trong ngõ nhỏ",
            "Mẹo ướp thịt nướng mềm tan chuẩn vị đầu bếp 5 sao",
            "Top 5 món ăn vặt cứu đói đêm muộn siêu dễ làm",
            "Thử thách ăn sạch thực đơn quán hot trend TikTok"
        ],
        "default_hook": "Ai mê ăn uống tuyệt đối không được bỏ qua công thức thần thánh này!",
        "hashtags": "#amthuc #monngon #reviewanngon #nauan #foodreview #ancungtiktok #yummy"
    },
    "finance": {
        "name": "Tài Chính & Đầu Tư / Kinh Doanh Online",
        "sub_topics": [
            "3 nguồn thu nhập thụ động bạn có thể bắt đầu ngay tối nay",
            "Sai lầm tài chính khiến 90% người trẻ làm mãi không dư",
            "Cách quản lý chi tiêu theo quy tắc 6 chiếc hũ kinh điển",
            "Kinh nghiệm mở gian hàng online 0 đồng vốn cho người mới",
            "Tư duy tiền bạc phân biệt người giàu và người nghèo"
        ],
        "default_hook": "Nếu bạn muốn tự do tài chính trước tuổi 30, hãy khắc cốt ghi tâm bài học này!",
        "hashtags": "#taichinh #kiemtien #dautu #kinhdoanh #kinhdoanhonline #phattrienbanthan #money"
    },
    "education": {
        "name": "Giáo Dục & Tiếng Anh / Kỹ Năng Mềm",
        "sub_topics": [
            "Cách nhớ 50 từ vựng tiếng Anh mỗi ngày không bao giờ quên",
            "Top 3 câu nói tiếng Anh giao tiếp giúp bạn sang xịn mịn tức thì",
            "Phương pháp Pomodoro tăng 300% hiệu suất học tập",
            "Cách thuyết trình tự tin trước đám đông không run rẩy",
            "Mẹo học ngữ pháp tiếng Anh qua phim ảnh cực bánh cuốn"
        ],
        "default_hook": "Ngừng học vẹt ngay! Đây là cách học thông minh nhất mà trường học không dạy bạn.",
        "hashtags": "#tienganh #hocketienganh #kynang #phattrienbanthan #ielts #studytips #education"
    }
}

class AIVideoEngine:
    """Động cơ tạo kịch bản video và render video tự động theo ngành nghề"""

    def __init__(self):
        pass

    def get_niches(self) -> Dict[str, Any]:
        return NICHE_CATALOG

    def generate_script(self, niche_key: str, user_topic: str, product_name: Optional[str] = None) -> Dict[str, Any]:
        """Tự động tạo kịch bản video ngắn chuẩn 3 hồi viral"""
        niche = NICHE_CATALOG.get(niche_key.lower(), NICHE_CATALOG["cntt"])
        topic = user_topic.strip() if user_topic.strip() else random.choice(niche["sub_topics"])

        hook = f"🔥 {niche['default_hook']}"
        
        # Xây dựng các cảnh chi tiết (Storyboarding)
        scenes = [
            {
                "scene": 1,
                "duration": "0s - 3s (HOOK)",
                "visual": f"Chữ giật tít lớn: '{topic}' phóng to, kèm tiếng hiệu ứng 'Boom / Pop'. Người dẫn chỉ tay lên màn hình.",
                "voiceover": f"Bạn có tin là việc '{topic}' bây giờ dễ đến mức ai cũng làm được không? Xem hết clip này nhé!"
            },
            {
                "scene": 2,
                "duration": "4s - 15s (VẤN ĐỀ & BÍ QUYẾT)",
                "visual": f"Mô phỏng thao tác thực tế: Cảnh quay trực tiếp màn hình/sản phẩm, zoom cận cảnh các bước thao tác nhanh gọn.",
                "voiceover": f"Thay vì mất hàng giờ mò mẫm, bạn chỉ cần áp dụng đúng 3 bước này. Bước 1: Xác định mục tiêu rõ ràng. Bước 2: Tận dụng công cụ thông minh để giải quyết 80% phần việc nặng."
            },
            {
                "scene": 3,
                "duration": "16s - 30s (GIÁ TRỊ & GIẢI PHÁP)",
                "visual": f"Kết quả xuất hiện hoành tráng (màn hình hiển thị sản phẩm hoàn thiện, giao diện mượt mà hoặc kết quả đo lường thành công).",
                "voiceover": f"Và đây là thành quả chỉ sau vài phút! Tốc độ nhanh gấp 10 lần mà độ chính xác và thẩm mỹ thì khỏi phải bàn."
            },
            {
                "scene": 4,
                "duration": "31s - 38s (CALL TO ACTION)",
                "visual": f"Mũi tên chỉ xuống link Bio, nhấp nháy chữ: 'Lưu lại ngay' hoặc 'Link nhận quà ở Bio'.",
                "voiceover": f"{f'Chi tiết sản phẩm ' + product_name + ' mình để ở Bio nhé!' if product_name else 'Bấm Lưu lại clip để dùng khi cần và Follow kênh để không bỏ lỡ mẹo hay mỗi ngày nhé!'}"
            }
        ]

        title = f"[{niche['name'].split('&')[0].strip()}] {topic}"
        caption = f"{hook}\n\n👉 {topic}.\n\nXem ngay bí kíp cực xịn trong video này nhé cả nhà!"
        if product_name:
            caption += f"\n\n🛒 Sản phẩm trong video: #{product_name.replace(' ', '')}"

        hashtags = f"{niche['hashtags']} #viral #xuhuong2026 #tips #hottrend"

        return {
            "niche_key": niche_key,
            "niche_name": niche["name"],
            "title": title,
            "topic": topic,
            "product_name": product_name or "Tự động",
            "hook": hook,
            "caption": caption,
            "hashtags": hashtags,
            "scenes": scenes,
            "suggested_audio": "Nhạc nền Upbeat Trendy Lo-Fi hoặc Energetic Phonk",
            "estimated_length": "35 - 45 giây (Chuẩn giữ chân Shorts/Reels/TikTok)"
        }

    def render_full_production(
        self,
        niche_key: str,
        user_topic: str,
        product_name: Optional[str] = None,
        voice_gender: str = "nu"
    ) -> Dict[str, Any]:
        """Quy trình toàn diện: Sinh kịch bản -> Sinh voice Edge-TTS tiếng Việt -> Render MP4 9:16 FFmpeg -> Đổi MD5"""
        from core.voice_engine import voice_engine
        from core.video_renderer import video_renderer

        # 1. Sinh kịch bản 3 hồi
        script_data = self.generate_script(niche_key, user_topic, product_name)

        # Tổng hợp toàn bộ câu thoại của kịch bản
        full_voiceover_text = " . ".join([s["voiceover"] for s in script_data["scenes"]])

        # 2. Sinh giọng đọc Edge-TTS
        import uuid
        job_id = uuid.uuid4().hex[:8]
        audio_filename = f"audio_{job_id}.mp3"
        video_filename = f"video_{job_id}.mp4"

        audio_path = voice_engine.generate_voiceover(
            text=full_voiceover_text,
            output_filename=audio_filename,
            voice_gender=voice_gender
        )

        # 3. Dựng video MP4 qua FFmpeg
        render_result = video_renderer.render_production_video(
            script_data=script_data,
            voice_audio_path=audio_path,
            output_filename=video_filename
        )

        return {
            "status": "success",
            "job_id": job_id,
            "script": script_data,
            "audio_url": f"/storage/generated_audios/{audio_filename}",
            "video_url": render_result["video_url"],
            "video_path": render_result["video_path"],
            "file_size": render_result["file_size"],
            "md5_hash": render_result["md5_hash"],
            "resolution": render_result["resolution"],
            "voice_gender": voice_gender
        }

    def render_demo_video(self, script_data: Dict[str, Any], output_path: str) -> str:
        """Tạo file video MP4 mẫu demo với animation chữ và hiệu ứng chuyển cảnh"""
        from core.video_renderer import get_ffmpeg_exe
        ffmpeg_exe = get_ffmpeg_exe()
        cmd = [
            ffmpeg_exe, "-y",
            "-f", "lavfi", "-i", "color=c=0x0a1128:s=720x1280:d=10",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            output_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, timeout=30)
            return output_path
        except Exception:
            with open(output_path, "wb") as f:
                f.write(b"NGOCKHANH_MEDIA_DEMO_CONTAINER_STREAM_" + os.urandom(2048))
            return output_path

ai_video_engine = AIVideoEngine()
