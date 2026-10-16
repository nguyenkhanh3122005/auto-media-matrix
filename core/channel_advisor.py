import os
import random
import time
from typing import Dict, Any, List, Optional

class ChannelAdvisor:
    """Cố vấn chiến lược xây kênh & Lập kế hoạch quảng bá sản phẩm tự động bằng AI"""

    def audit_channel(self, channel_id: str, platform: str = "tiktok", screenshot_note: Optional[str] = None) -> Dict[str, Any]:
        """Phân tích, chấm điểm và đưa ra ý kiến xây kênh chi tiết"""
        clean_id = channel_id.strip() if channel_id.strip() else "@my_channel"
        
        # Điểm đánh giá giả lập dựa trên thuật toán phân tích kênh 2026
        profile_score = random.randint(65, 82)
        content_score = random.randint(58, 76)
        engagement_score = random.randint(60, 85)
        overall_score = int((profile_score + content_score + engagement_score) / 3)

        diagnosis = []
        if overall_score < 70:
            diagnosis.append("⚠️ Bio kênh còn chung chung, chưa nêu bật giá trị cốt lõi hoặc lý do người xem phải bấm Follow.")
            diagnosis.append("⚠️ 3 giây đầu của video (Hook) chưa đủ giật tít, tỷ lệ rớt người xem (drop-off) sau 5s đầu còn cao.")
            diagnosis.append("⚠️ Tần suất đăng chưa đồng đều; cần duy trì khung giờ cố định để thuật toán ghi nhận thói quen.")
        else:
            diagnosis.append("✅ Định vị kênh khá tốt, phong cách thumbnail bắt đầu có sự đồng bộ.")
            diagnosis.append("💡 Cần tăng cường kêu gọi tương tác (CTA 2 chiều) ở phần bình luận để đẩy video vào luồng thịnh hành.")
            diagnosis.append("💡 Nên gắn thêm link Bio thông minh (Landing page / Zalo / Bio link) để chuyển đổi người xem thành khách hàng.")

        actionable_steps = [
            "1. Tối ưu lại phần Tiểu sử (Bio): Cấu trúc [Bạn là ai] + [Giá trị chia sẻ] + [Lời kêu gọi bấm vào link quà tặng/sản phẩm].",
            "2. Chuẩn hóa 3 giây đầu tiên (Hook): Bắt buộc dùng câu hỏi gây tò mò hoặc số liệu gây sốc trong 3s đầu.",
            "3. Áp dụng quy tắc ma trận nội dung 70 - 20 - 10: 70% video trao giá trị ngách, 20% video bắt trend, 10% video bán hàng trực diện.",
            "4. Tương tác với đối thủ: Dành 15 phút mỗi ngày đi bình luận có chuyên môn dưới các clip triệu view cùng ngành để hút tệp follow tự nhiên."
        ]

        target_niche_suggestions = [
            {"pillar": "Video Phễu (Viral Hook)", "ratio": "50%", "purpose": "Thu hút lượt xem lớn từ người chưa follow"},
            {"pillar": "Video Chuyên Môn / Review", "ratio": "30%", "purpose": "Xây dựng lòng tin, chứng minh chất lượng sản phẩm"},
            {"pillar": "Video Chuyển Đổi (Bán Hàng)", "ratio": "20%", "purpose": "Kêu gọi inbox / mua hàng qua link Bio"}
        ]

        return {
            "channel_id": clean_id,
            "platform": platform.upper(),
            "overall_score": overall_score,
            "sub_scores": {
                "profile_optimization": profile_score,
                "content_retention": content_score,
                "engagement_power": engagement_score
            },
            "status": "Cần Tối Ưu Hóa Thuật Toán",
            "diagnosis": diagnosis,
            "actionable_steps": actionable_steps,
            "content_pillars": target_niche_suggestions,
            "analyzed_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

    def generate_30day_product_matrix(self, channel_id: str, product_name: str, niche: str = "general") -> List[Dict[str, Any]]:
        """Lập ma trận 30 ngày xây kênh quảng bá sản phẩm tự động"""
        prod = product_name.strip() if product_name.strip() else "Sản phẩm / Dịch vụ của bạn"
        
        matrix = []
        weeks = [
            ("Tuần 1: Nhận Diện Vấn Đề & Hút Tệp Khách Hàng", "Thu hút người xem có nhu cầu ngầm"),
            ("Tuần 2: Xây Dựng Niềm Tin & Chuyên Gia", "Chia sẻ bí quyết, so sánh, chứng minh năng lực"),
            ("Tuần 3: Trải Nghiệm & Bằng Chứng Khách Hàng (Social Proof)", "Feedback, unboxing, giải đáp thắc mắc"),
            ("Tuần 4: Chốt Đơn & Bùng Nổ Doanh Số (Conversion)", "Ưu đãi giới hạn, quà tặng độc quyền")
        ]

        sample_titles = [
            f"Sự thật bất ngờ về cách giải quyết vấn đề bằng {prod}",
            f"Sai lầm 99% người gặp phải khi chọn mua {prod}",
            f"Review chân thực sau 14 ngày sử dụng {prod} - Có đáng tiền không?",
            f"So sánh {prod} với các giải pháp truyền thống trên thị trường",
            f"Bí mật hậu trường tạo ra {prod} mà bạn chưa từng nghe",
            f"Khách hàng nói gì về {prod}? Trải nghiệm thực tế 100%",
            f"Hướng dẫn từ A đến Z cách sử dụng {prod} đạt hiệu quả gấp 3 lần",
            f"Ưu đãi độc quyền dành riêng cho người xem video này về {prod}"
        ]

        day_count = 30
        for day in range(1, day_count + 1):
            week_idx = min(3, (day - 1) // 7)
            title = sample_titles[(day - 1) % len(sample_titles)] + f" (Phần {day})"
            video_type = "Video Phễu" if week_idx == 0 else ("Video Chuyên Môn" if week_idx == 1 else ("Video Review & Feedback" if week_idx == 2 else "Video Bán Hàng"))
            
            matrix.append({
                "day": day,
                "week_theme": weeks[week_idx][0],
                "video_type": video_type,
                "title": title,
                "golden_hour": "11:30" if day % 2 == 0 else "19:45",
                "cta_strategy": f"Gắn thẻ #{prod.replace(' ', '')} & kêu gọi bấm vào link Bio để nhận tài liệu/ưu đãi",
                "status": "scheduled" if day <= 3 else "planned"
            })

        return matrix

channel_advisor = ChannelAdvisor()
