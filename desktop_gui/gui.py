import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import webbrowser
import time
import sys
from pathlib import Path

# Thêm thư mục gốc vào path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.db import db
from scheduler.task_runner import task_runner
from core.video_processor import video_processor
from config import SERVER_HOST, SERVER_PORT

class AutoVibeDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NGỌC KHÁNH MEDIA - Desktop Control Center")
        self.root.geometry("850x620")
        self.root.configure(bg="#0c1017")

        self.setup_styles()
        self.create_widgets()
        self.load_accounts()

        # Đăng ký listener nhận log từ task runner
        task_runner.register_log_listener(self.append_log_entry)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#0c1017", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00f0ff")
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)
        style.configure("Treeview", 
                        background="#161f30", 
                        foreground="#f8fafc", 
                        fieldbackground="#161f30", 
                        rowheight=26,
                        font=("Segoe UI", 9))
        style.map("Treeview", background=[("selected", "#0284c7")])

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#121824", height=60, padx=15, pady=10)
        header_frame.pack(fill="x")
        
        lbl_title = ttk.Label(header_frame, text="⚡ NGỌC KHÁNH MEDIA CONTROL", style="Header.TLabel", background="#121824")
        lbl_title.pack(side="left")

        btn_web = tk.Button(header_frame, text="🌐 Mở Web Dashboard", bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"),
                            command=self.open_web_dashboard, relief="flat", padx=10, pady=4, cursor="hand2")
        btn_web.pack(side="right")

        # Main Layout
        content_frame = tk.Frame(self.root, bg="#0c1017", padx=15, pady=10)
        content_frame.pack(fill="both", expand=True)

        # Bảng danh sách tài khoản
        lbl_acc = ttk.Label(content_frame, text="Danh Sách Tài Khoản & Kênh:")
        lbl_acc.pack(anchor="w", pady=(0, 5))

        columns = ("id", "name", "platform", "method", "status", "actions")
        self.tree = ttk.Treeview(content_frame, columns=columns, show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Tên Kênh")
        self.tree.heading("platform", text="Nền Tảng")
        self.tree.heading("method", text="Cơ Chế")
        self.tree.heading("status", text="Trạng Thái")
        self.tree.heading("actions", text="Lượt Tương Tác")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=180)
        self.tree.column("platform", width=100, anchor="center")
        self.tree.column("method", width=110, anchor="center")
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("actions", width=100, anchor="center")
        self.tree.pack(fill="x", pady=(0, 10))

        # Action Buttons
        btn_bar = tk.Frame(content_frame, bg="#0c1017")
        btn_bar.pack(fill="x", pady=5)

        btn_nurture_selected = tk.Button(btn_bar, text="▶ Nuôi Nick Đã Chọn", bg="#059669", fg="white",
                                         font=("Segoe UI", 9, "bold"), command=self.nurture_selected, relief="flat", padx=12, pady=6)
        btn_nurture_selected.pack(side="left", padx=(0, 10))

        btn_nurture_all = tk.Button(btn_bar, text="🔥 Nuôi Tất Cả Nick", bg="#0d9488", fg="white",
                                    font=("Segoe UI", 9, "bold"), command=self.nurture_all, relief="flat", padx=12, pady=6)
        btn_nurture_all.pack(side="left", padx=(0, 10))

        btn_mod_md5 = tk.Button(btn_bar, text="🛠️ Lách Bản Quyền / Đổi MD5 Video", bg="#d97706", fg="white",
                                font=("Segoe UI", 9, "bold"), command=self.quick_mod_md5, relief="flat", padx=12, pady=6)
        btn_mod_md5.pack(side="left", padx=(0, 10))

        btn_refresh = tk.Button(btn_bar, text="🔄 Làm Mới", bg="#334155", fg="white",
                                font=("Segoe UI", 9), command=self.load_accounts, relief="flat", padx=10, pady=6)
        btn_refresh.pack(side="right")

        # Terminal Log Box
        lbl_log = ttk.Label(content_frame, text="Nhật Ký Thực Thi (Terminal Log):")
        lbl_log.pack(anchor="w", pady=(10, 5))

        self.log_text = tk.Text(content_frame, bg="#05080f", fg="#38bdf8", font=("Consolas", 9), height=10, relief="flat", padx=10, pady=8)
        self.log_text.pack(fill="both", expand=True)

    def load_accounts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        accounts = db.get_accounts()
        for acc in accounts:
            self.tree.insert("", "end", values=(
                acc["id"], acc["name"], acc["platform"].upper(), acc["method"], acc["status"], acc["actions_count"]
            ))

    def log(self, message: str):
        self.log_text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see("end")

    def append_log_entry(self, entry: dict):
        msg = f"[{entry.get('status', 'info').upper()}] {entry.get('account_name', '')}: {entry.get('action', '')} - {entry.get('details', '')}"
        self.root.after(0, self.log, msg)

    def open_web_dashboard(self):
        webbrowser.open(f"http://{SERVER_HOST}:{SERVER_PORT}")

    def nurture_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn 1 tài khoản trong danh sách trước!")
            return
        item = self.tree.item(selected[0])
        acc_id = item["values"][0]
        acc_name = item["values"][1]
        self.log(f"Đang bắt đầu nuôi tài khoản {acc_name}...")
        task_runner.start_background_nurture(acc_id, actions=15)

    def nurture_all(self):
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn nuôi toàn bộ tài khoản?"):
            self.log("Bắt đầu kịch bản nuôi toàn bộ tài khoản...")
            task_runner.start_background_nurture(None, actions=10)

    def quick_mod_md5(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.avi *.mkv")])
        if not file_path:
            return
        self.log(f"Đang xử lý lách bản quyền cho: {file_path}")
        output_file, old_md5, new_md5 = video_processor.modify_md5_fast(file_path)
        self.log(f"Thành công! MD5 cũ: {old_md5} -> MD5 mới: {new_md5}")
        self.log(f"Đã lưu video lách bản quyền tại: {output_file}")
        messagebox.showinfo("Hoàn tất", f"Đã đổi MD5 thành công!\nMD5 cũ: {old_md5}\nMD5 mới: {new_md5}\n\nTệp lưu tại:\n{output_file}")

def main():
    root = tk.Tk()
    app = AutoVibeDesktopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
