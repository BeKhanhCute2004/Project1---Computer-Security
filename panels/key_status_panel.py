import tkinter as tk
from tkinter.simpledialog import askstring
import json
import hashlib
from utils.crypto_utils import generate_rsa_keys
from config import USER_DB
import os
from datetime import datetime

class KeyStatusPanel(tk.Frame):
    def __init__(self, master, user_email=None):
        super().__init__(master)
        self.user_email = user_email

        tk.Label(self, text="Trạng thái khóa RSA", font=("Segoe UI", 14)).pack(pady=10)

        # Thêm frame chứa text và scrollbar
        text_frame = tk.Frame(self)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5) # lắp đầy cả chiều rộng và chiều cao của frame cha, thêm khoảng cách 10px và 5px cho các cạnh

        self.output = tk.Text(text_frame, width=60, height=10, wrap="word")
        self.output.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.output.yview) # gọi yview() để kết nối scrollbar với self.output
        scrollbar.pack(side="right", fill="y")
        self.output.config(yscrollcommand=scrollbar.set) # khi nội dung text thay đổi, scrollbar sẽ tự động cập nhật vị trí cuộn

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=6)
        tk.Button(btn_frame, text="Làm mới", command=self.load_info).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Làm mới khóa", command=self.renew_key).pack(side="left", padx=5)
        self.load_info()

    def load_info(self):
        self.output.delete(1.0, tk.END) # xoá mọi thứ từ dòng 1 cột 0 đến hết (END) trong text widget
        path = f"rsa_keys/{self.user_email}_info.json"
        if not os.path.exists(path):
            self.output.insert(tk.END, "Không tìm thấy thông tin khóa.")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        expires = data.get("expires")
        try:
            exp_date = datetime.strptime(expires, "%Y-%m-%d") # chuyển đổi chuỗi ngày tháng sang đối tượng datetime
            days_left = (exp_date - datetime.now()).days
        except Exception:
            days_left = None

        lines = [
            f"Email: {data['email']}",
            f"Ngày tạo: {data['created']}",
            f"Hết hạn: {data['expires']}",
            f"Public Key: {data['public_key_file']}",
            f"Private Key (mã hóa): {data['private_key_file']}"
        ]
        if days_left is not None:
            if days_left < 0:
                lines.append("Khóa đã hết hạn! Vui lòng làm mới.")
            elif days_left <= 7:
                lines.append(f"Khóa sắp hết hạn ({days_left} ngày nữa). Nên làm mới khóa.")
            else:
                lines.append(f"Còn {days_left} ngày trước khi hết hạn.")
        self.output.insert(tk.END, "\n".join(lines))

    def renew_key(self):
        pw = askstring("Xác nhận", "Nhập passphrase để tạo lại khóa:", show="*")
        if not pw:
            return
        # Xác thực passphrase
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
            user = users[self.user_email]
            salt = user["salt"]
            pw_hash = hashlib.sha256((pw + salt).encode()).hexdigest()
            if pw_hash != user["pass_hash"]:
                tk.messagebox.showerror("Lỗi", "Passphrase không chính xác.")
                return
            generate_rsa_keys(self.user_email, pw)
            tk.messagebox.showinfo("Thành công", "Đã tạo lại khóa mới!")
            self.load_info()
        except Exception as e:
            tk.messagebox.showerror("Lỗi", f"Làm mới khóa thất bại: {e}")