import random
import os
import requests
from typing import Dict, Any
from config import GEMINI_API_KEY, OPENAI_API_KEY, AI_PROVIDER

NICHE_TEMPLATES = {
    "general": {
        "hooks": [
            "Xem đến cuối để không bỏ lỡ điều bất ngờ này nhé!",
            "Bạn đã biết bí mật này chưa? Cùng xem ngay!",
            "Cái này cuốn thực sự, không xem phí cả thanh xuân 😂",
            "Mẹo hay mỗi ngày dành riêng cho bạn đây!",
            "Thử ngay cách này nhé cả nhà, hiệu quả bất ngờ luôn."
        ],
        "tags": ["#xuhuong", "#fyp", "#viral", "#trendingtiktok", "#xuhuong2026", "#hot"]
    },
    "entertainment": {
        "hooks": [
            "Cười xỉu với pha xử lý đỉnh cao này 😂",
            "Đố bạn nhịn được cười đến giây cuối cùng 🤣",
            "Xem đi xem lại vẫn thấy hài hước!",
            "Đúng là nhân tài ẩn dật mà 😆"
        ],
        "tags": ["#haihuoc", "#giaitri", "#cuoivobung", "#funny", "#xuhuong", "#meme"]
    },
    "tech": {
        "hooks": [
            "Tính năng cực kỳ hữu ích mà 90% mọi người chưa biết!",
            "Mẹo công nghệ giúp bạn tiết kiệm hàng giờ mỗi ngày 🔥",
            "Review chân thực nhất dành cho anh em đam mê công nghệ.",
            "Bí kíp tối ưu cực hay nên lưu lại dùng dần nhé!"
        ],
        "tags": ["#congnghe", "#tips", "#techvn", "#review", "#meohay", "#laptrinh"]
    },
    "finance": {
        "hooks": [
            "Cách tạo thêm dòng thu nhập thứ 2 đơn giản và hiệu quả.",
            "Tư duy tài chính giúp bạn thay đổi hoàn toàn cuộc sống 💡",
            "Đừng để tiền nhàn rỗi, hãy xem ngay bài học này!",
            "Bí quyết quản lý chi tiêu và đầu tư khôn ngoan."
        ],
        "tags": ["#taichinh", "#kiemtien", "#dautu", "#kinhdoanh", "#kinhdoanhonline", "#phattrienbanthan"]
    }
}

class AIGenerator:
    """Tự động sinh tiêu đề, caption giật tít và hashtag viral theo chủ đề video"""

    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.openai_key = OPENAI_API_KEY

    def generate_viral_content(self, title: str, niche: str = "general", platform: str = "tiktok") -> Dict[str, str]:
        """Tạo caption & hashtag tối ưu cho thuật toán nền tảng"""
        # Nếu có Gemini API Key
        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                prompt = (
                    f"Viết 1 đoạn caption ngắn hấp dẫn (dưới 150 ký tự) và 5-8 hashtag thịnh hành cho video '{title}' "
                    f"trên nền tảng {platform}, chủ đề {niche}. Định dạng trả về: Caption: [nội dung] | Hashtags: [#tag1 #tag2 ...]"
                )
                res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=10)
                text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                if "|" in text:
                    parts = text.split("|")
                    caption = parts[0].replace("Caption:", "").strip()
                    hashtags = parts[1].replace("Hashtags:", "").strip()
                    return {"caption": caption, "hashtags": hashtags}
            except Exception:
                pass

        # Template Engine thông minh nội bộ (100% không phụ thuộc internet/API key)
        niche_data = NICHE_TEMPLATES.get(niche.lower(), NICHE_TEMPLATES["general"])
        hook = random.choice(niche_data["hooks"])
        tags = " ".join(random.sample(niche_data["tags"], min(4, len(niche_data["tags"]))))
        
        # Thêm hashtag riêng theo nền tảng
        if platform == "tiktok":
            tags += " #fyp #tiktokvietnam"
        elif platform == "facebook":
            tags += " #reels #facebookreels"
        elif platform == "youtube":
            tags += " #shorts #youtubeshorts"

        caption = f"{title} - {hook}"
        return {
            "caption": caption,
            "hashtags": tags
        }

ai_generator = AIGenerator()
