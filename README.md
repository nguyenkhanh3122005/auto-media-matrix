# ⚡ AutoVibe Media Matrix 2026

> **Hệ thống tự động hóa nuôi nick & đăng video đa nền tảng (TikTok, Facebook Reels, YouTube Shorts)**  
> Hỗ trợ 3 cơ chế chạy: **Trình duyệt độc lập (Playwright Profile)** + **Antidetect Browser (AdsPower/Hidemyacc API)** + **Giả lập Android (LDPlayer/ADB)**.  
> Tích hợp 3 giao diện: **Web Dashboard Cyberpunk**, **Desktop App GUI**, và **CLI Headless Runner**.

---

## 🚀 Các Tính Năng Đỉnh Cao (Vibe Features)

### 1. 🛡️ Cơ Chế Vận Hành Linh Hoạt (3-in-1)
* **Playwright Persistent Context (Built-in)**: Mỗi tài khoản lưu trữ cookie, session đăng nhập và fingerprint độc lập trong thư mục `storage/profiles/{acc_name}`. Hỗ trợ gắn **Proxy riêng** cho từng nick để chống checkpoint/trùng IP.
* **Antidetect Browser Connector**: Kết nối trực tiếp qua Local API tới **AdsPower**, **GoLogin**, **Hidemyacc** để điều khiển profile antidetect có sẵn.
* **Android ADB Controller**: Kết nối và điều khiển giả lập **LDPlayer / Nox** hoặc điện thoại Android thật cắm cáp USB (vuốt màn hình, chạm 2 lần thả tim, đẩy video vào thư viện).

### 2. 🤖 Kịch Bản Nuôi Nick Tự Nhiên (Human-like Warm-up)
* Lướt video For You Page / Reels / Shorts với thời gian ngẫu nhiên từ **12 - 38 giây**.
* Tự động điều chỉnh hành vi theo con người:
  * Xác suất thả tim: **25%**
  * Xác suất bình luận: **8%** (chọn mẫu bình luận khen tự nhiên theo chủ đề)
  * Giãn cách giữa các thao tác để tránh bị quét spam/shadowban.

### 3. 🎬 Tự Động Hóa Đăng Video & Lách Bản Quyền
* **Fast MD5 Modifier**: Thay đổi mã băm MD5 / SHA256 của file video trong **0.01 giây** (bằng kỹ thuật binary container padding, không làm giảm chất lượng video hay tốn CPU render).
* **Bộ lọc FFmpeg (Nâng cao)**: Tự động đổi nhẹ tốc độ (1.02x), chỉnh pitch âm thanh, zoom 2% và xóa sạch toàn bộ metadata Exif camera cũ.
* **AI Caption & Hashtag Generator**: Tự động sinh tiêu đề giật tít (hook) và các hashtag viral thịnh hành theo từng ngách (`#xuhuong`, `#fyp`, `#reels`, `#shorts`).

---

## 📂 Cấu Trúc Dự Án

```
auto-media-matrix/
├── START-WEB-DASHBOARD.bat    # [1-Click] Khởi động Web Dashboard (http://127.0.0.1:8088)
├── START-DESKTOP-APP.bat      # [1-Click] Khởi động Giao diện Desktop Windows
├── INSTALL-REQUIREMENTS.bat   # [1-Click] Cài đặt toàn bộ thư viện & Playwright Chromium
├── backend/
│   └── app.py                 # FastAPI Server + WebSocket Live Streaming Log
├── web_dashboard/
│   └── index.html             # Giao diện Web Cyberpunk Dark Mode (Vue 3 + TailwindCSS)
├── desktop_gui/
│   └── gui.py                 # Giao diện Desktop GUI (Python Tkinter dark theme)
├── cli_runner.py              # Bộ điều khiển dòng lệnh Terminal / Cron
├── core/
│   ├── browser_manager.py     # Quản lý trình duyệt chống phát hiện & Proxy
│   ├── antidetect_api.py      # Kết nối AdsPower / GoLogin / Hidemyacc API
│   ├── adb_manager.py         # Điều khiển LDPlayer & Android qua ADB
│   ├── video_processor.py     # Thay đổi MD5 & xử lý lách bản quyền video
│   └── ai_generator.py        # Sinh caption & hashtag viral
├── engines/
│   ├── tiktok_engine.py       # Động cơ nuôi nick & up video TikTok
│   ├── facebook_engine.py     # Động cơ nuôi nick & up FB Reels
│   └── youtube_engine.py      # Động cơ nuôi nick & up YouTube Shorts
├── database/
│   └── db.py                  # Cơ sở dữ liệu SQLite quản lý tài khoản & video
└── storage/
    ├── profiles/              # Lưu trữ cookies & session trình duyệt
    ├── videos/                # Video tải lên
    └── processed_videos/      # Video đã lách bản quyền & đổi MD5
```

---

## 🛠️ Hướng Dẫn Sử Dụng Nhanh

### Bước 1: Cài Đặt Môi Trường
Nhấp đúp chuột vào file:
```
INSTALL-REQUIREMENTS.bat
```
*(Hoặc chạy lệnh `pip install -r requirements.txt && playwright install chromium`)*

### Bước 2: Khởi Chạy Giao Diện

#### Cách 1: Web Dashboard (Khuyên dùng - Đẹp & Trực quan nhất)
Nhấp đúp vào:
```
START-WEB-DASHBOARD.bat
```
Trình duyệt sẽ tự động mở trang quản trị tại: `http://127.0.0.1:8088`. Tại đây bạn có thể:
1. Thêm tài khoản mới (chọn TikTok, Facebook hoặc YouTube).
2. Tải video MP4 lên -> AI sẽ tự động viết caption & gắn hashtag.
3. Bấm **"Nuôi Tất Cả Nick"** hoặc **"Đăng Hàng Đợi Video"**.
4. Theo dõi **Live Logs** thời gian thực hiển thị từng hành động lướt, like, comment.

#### Cách 2: Desktop App (Giao diện phần mềm Windows)
Nhấp đúp vào:
```
START-DESKTOP-APP.bat
```
Giao diện ứng dụng cửa sổ Windows sẽ xuất hiện, cho phép bạn chọn nick, bấm nuôi, hoặc bấm nút **"Lách Bản Quyền / Đổi MD5 Video"** cực nhanh.

#### Cách 3: Chạy Dòng Lệnh (CLI / VPS / Cronjob)
Mở PowerShell hoặc Command Prompt tại thư mục dự án:
```powershell
# Liệt kê tài khoản:
python cli_runner.py --list-accounts

# Nuôi toàn bộ tài khoản:
python cli_runner.py --nurture-all --actions 15

# Nuôi 1 tài khoản cụ thể theo ID:
python cli_runner.py --nurture 1

# Đăng ngay các video trong hàng đợi:
python cli_runner.py --upload-queue

# Lách bản quyền / Đổi MD5 1 video bất kỳ:
python cli_runner.py --mod-md5 "C:\path\to\video.mp4"
```

---

## 🔐 Lưu Ý Về Đăng Nhập & Bảo Mật Nick

1. **Lần đầu đăng nhập profile**:
   - Khi chạy nuôi nick lần đầu bằng phương thức `browser`, trình duyệt Chromium sẽ mở ra. Bạn chỉ cần đăng nhập tài khoản một lần duy nhất.
   - Trình duyệt sẽ lưu toàn bộ Cookie và Session vào thư mục `storage/profiles/{ten_tai_khoan}`. Từ các lần sau, tài khoản sẽ luôn ở trạng thái đã đăng nhập.
2. **Sử dụng Proxy**:
   - Để nuôi nhiều tài khoản an toàn không bị khóa chéo, hãy nhập proxy định dạng `user:pass@ip:port` khi thêm tài khoản.
3. **Giả lập Android**:
   - Nếu bạn dùng LDPlayer, hãy bật tính năng **ADB Debug** trong Cài đặt LDPlayer. Hệ thống sẽ tự động nhận diện thiết bị qua cổng ADB.

Chúc bạn xây dựng dàn ma trận kênh triệu view thành công rực rỡ! 🚀
