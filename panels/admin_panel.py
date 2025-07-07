import tkinter as tk
from tkinter import scrolledtext
import json
from config import USER_DB, LOG_FILE, log_event

class AdminFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Menu trái
        menu = tk.Frame(self)
        menu.pack(side="left", fill="y")

        btns = [
            ("Xem danh sách tài khoản", self.show_users),
            ("Xem log hệ thống", self.show_logs),
            ("Đăng xuất", self.logout)
        ]

        for text, cmd in btns:
            tk.Button(menu, text=text, width=20, command=cmd).pack(pady=5)

        # Nội dung phải
        self.content = tk.Frame(self)
        self.content.pack(side="right", expand=True, fill="both")

        # Mặc định hiện danh sách tài khoản
        self.show_users()

    def show_users(self):
        self.clear_content()

        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        headers = ["Email", "Họ tên", "Ngày sinh", "Địa chỉ", "SĐT", "Trạng thái", "Hành động"]
        table = tk.Frame(self.content)
        table.pack(padx=10, pady=10)

        # Header
        for i, head in enumerate(headers):
            tk.Label(table, text=head, font=("Segoe UI", 10, "bold"), borderwidth=1, relief="solid", width=28).grid(row=0, column=i)

        # Data rows
        for row_idx, (email, data) in enumerate(users.items(), start=1):
            name = data.get("name", "")
            dob = data.get("dob", "")
            address = data.get("address", "")
            phone = data.get("phone", "")
            status = data.get("status", "active")

            values = [email, name, dob, address, phone, status]

            for col_idx, val in enumerate(values):
                tk.Label(table, text=val, borderwidth=1, relief="solid", width=28, anchor="w").grid(row=row_idx, column=col_idx, sticky="nsew", pady=0)

            # Nút khoá/mở
            action_text = "Mở tài khoản" if status == "locked" else "Khoá tài khoản"
            action_btn = tk.Button(table, text=action_text,
                                command=lambda e=email: self.toggle_account_status(e))
            action_btn.grid(row=row_idx, column=len(headers) - 1, pady=0)

    def toggle_account_status(self, email):
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)

            if email not in users:
                return

            current = users[email].get("status", "active")
            new_status = "locked" if current == "active" else "active"
            users[email]["status"] = new_status

            with open(USER_DB, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2, ensure_ascii=False)

            log_event(f"Admin cập nhật trạng thái tài khoản: {email} thành {new_status}")
            self.show_users()  # Refresh giao diện
        except Exception as e:
            tk.messagebox.showerror("Lỗi", f"Lỗi khi cập nhật: {str(e)}")

    def show_logs(self):
        self.clear_content()

        text_frame = tk.Frame(self.content)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.output = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.output.pack(fill="both", expand=True)

        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = f.read()
            self.output.insert(tk.END, logs)
        except FileNotFoundError:
            self.output.insert(tk.END, "Chưa có log nào.")

    def clear_content(self):
        # Xóa nội dung bên phải
        for widget in self.content.winfo_children(): 
            widget.destroy()

    def logout(self):
        self.clear_content()
        # Đặt lại user hiện tại và quay về màn hình đăng nhập
        self.master.current_user = None
        self.master.show_frame("LoginFrame")
