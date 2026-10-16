import sys
import os
from pathlib import Path

# Đảm bảo UTF-8 trên Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent))

from database.db import db

def seed():
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM accounts")
        conn.commit()

    sample_accounts = [
        {"name": "nguyễn duy", "platform": "facebook", "followers": 0, "proxy": "Dùng IP máy / 50ms", "date": "1/10/2026"},
        {"name": "QUETUDUY", "platform": "youtube", "followers": 0, "proxy": "Dùng IP máy / 50ms", "date": "25/9/2026"},
        {"name": "hgboo213", "platform": "tiktok", "followers": 0, "proxy": "Dùng IP máy / 50ms", "date": "1/10/2026"},
        {"name": "quetuduy", "platform": "facebook", "followers": 0, "proxy": "Dùng IP máy / 50ms", "date": "25/9/2026"},
        {"name": "quetuduy", "platform": "tiktok", "followers": 0, "proxy": "Dùng IP máy / 50ms", "date": "28/9/2026"},
    ]

    for acc in sample_accounts:
        # Avoid duplicate name constraints by qualifying if needed or inserting
        name = f"({acc['platform'].upper()}): {acc['name']}"
        db.add_account(
            name=name,
            platform=acc["platform"],
            method="browser",
            profile_id=f"profile_{acc['platform']}_{acc['name']}",
            proxy=acc["proxy"],
            niche="general"
        )
    
    db.add_log("Khởi tạo dàn kênh", "success", "Đã nạp sẵn 5 kênh mẫu như giao diện BAOX AI")
    print("[OK] Đã nạp 5 tài khoản chuẩn khớp ảnh demo!")

if __name__ == "__main__":
    seed()
