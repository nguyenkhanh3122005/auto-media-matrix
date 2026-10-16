import os
from pathlib import Path

# Thư mục gốc dự án
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "storage"
PROFILES_DIR = DATA_DIR / "profiles"
VIDEOS_DIR = DATA_DIR / "videos"
PROCESSED_VIDEOS_DIR = DATA_DIR / "processed_videos"
GENERATED_VIDEOS_DIR = DATA_DIR / "generated_videos"
GENERATED_AUDIOS_DIR = DATA_DIR / "generated_audios"
DB_PATH = DATA_DIR / "matrix.db"

# Đảm bảo các thư mục tồn tại
for directory in [DATA_DIR, PROFILES_DIR, VIDEOS_DIR, PROCESSED_VIDEOS_DIR, GENERATED_VIDEOS_DIR, GENERATED_AUDIOS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Cấu hình Server & Web Dashboard
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8088

# Cấu hình Antidetect Browser Local API
ADSPOWER_API_URL = "http://local.adspower.net:50325"
GOLOGIN_API_URL = "http://127.0.0.1:36949"
HIDEMYACC_API_URL = "http://127.0.0.1:5000"

# Đường dẫn LDPlayer / ADB phổ biến trên Windows
POSSIBLE_ADB_PATHS = [
    "adb", # Nếu đã có trong PATH
    r"C:\leidian\LDPlayer9\adb.exe",
    r"D:\leidian\LDPlayer9\adb.exe",
    r"C:\LDPlayer\LDPlayer9\adb.exe",
    r"D:\LDPlayer\LDPlayer9\adb.exe",
    r"C:\Program Files\Nox\bin\adb.exe",
    r"C:\Program Files (x86)\Nox\bin\adb.exe",
]

# Cấu hình AI sinh tiêu đề & hashtag
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini") # "gemini" | "openai" | "template"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Kịch bản nuôi mặc định (Human-like behavior)
DEFAULT_NURTURE_CONFIG = {
    "min_watch_seconds": 12,
    "max_watch_seconds": 38,
    "like_probability": 0.25,        # 25% cơ hội thả tim
    "comment_probability": 0.08,     # 8% cơ hội bình luận
    "follow_probability": 0.05,      # 5% cơ hội follow
    "total_actions_per_session": 20, # Mỗi phiên lướt 20 video
    "delay_between_actions": (3, 8), # Nghỉ giữa các thao tác 3 - 8s
}

# Mẫu bình luận tự nhiên theo chủ đề
COMMENT_TEMPLATES = [
    "Quá hay luôn ạ! 🔥",
    "Nội dung bánh cuốn ghê 😍",
    "Tuyệt vời quá bạn ơi 👏",
    "Chia sẻ thêm nhiều nữa nha!",
    "Đỉnh chóp luôn á ❤️",
    "Thả tim cho clip xịn sò này nhé ✨",
    "Rất hữu ích, cảm ơn bạn nhiều!",
    "Video chất lượng thật sự 💯",
    "Hay quá ad ơi, hóng phần tiếp theo!",
    "Chuẩn luôn nè 😄"
]
