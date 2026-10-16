import argparse
import asyncio
import sys
import os
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.append(str(Path(__file__).resolve().parent))

from database.db import db
from scheduler.task_runner import task_runner
from core.video_processor import video_processor

def main():
    parser = argparse.ArgumentParser(description="AutoVibe Media Matrix - Headless CLI Controller")
    parser.add_argument("--list-accounts", action="store_true", help="Liệt kê toàn bộ tài khoản trong hệ thống")
    parser.add_argument("--nurture-all", action="store_true", help="Chạy nuôi toàn bộ tài khoản")
    parser.add_argument("--nurture", type=int, help="Chạy nuôi 1 tài khoản theo ID")
    parser.add_argument("--actions", type=int, default=15, help="Số lượng video lướt mỗi phiên (Mặc định 15)")
    parser.add_argument("--upload-queue", action="store_true", help="Chạy hàng đợi đăng video ngay lập tức")
    parser.add_argument("--mod-md5", type=str, help="Thay đổi MD5 lách bản quyền cho 1 video")

    args = parser.parse_args()

    if args.list_accounts:
        accounts = db.get_accounts()
        print("\n================ MA TRẬN TÀI KHOẢN ================")
        for acc in accounts:
            print(f"ID: {acc['id']:<3} | Tên: {acc['name']:<18} | Platform: {acc['platform'].upper():<10} | Cơ chế: {acc['method']:<10} | Status: {acc['status']}")
        print("===================================================\n")
        return

    if args.mod_md5:
        print(f"[*] Đang thay đổi MD5 cho: {args.mod_md5}")
        out_p, old_h, new_h = video_processor.modify_md5_fast(args.mod_md5)
        print(f"[✓] Thành công!\n- MD5 gốc: {old_h}\n- MD5 mới: {new_h}\n- File mới: {out_p}")
        return

    if args.nurture_all:
        print(f"[*] Đang bắt đầu nuôi toàn bộ tài khoản ({args.actions} lượt/acc)...")
        asyncio.run(task_runner.run_nurture_all(args.actions))
        print("[✓] Hoàn thành phiên nuôi!")
        return

    if args.nurture:
        print(f"[*] Đang bắt đầu nuôi tài khoản ID #{args.nurture}...")
        asyncio.run(task_runner.execute_nurture(args.nurture, args.actions))
        print("[✓] Hoàn thành phiên nuôi!")
        return

    if args.upload_queue:
        print("[*] Đang kiểm tra và đẩy video trong hàng đợi lên nền tảng...")
        asyncio.run(task_runner.execute_upload_queue())
        print("[✓] Hoàn thành đẩy video!")
        return

    parser.print_help()

if __name__ == "__main__":
    main()
