import tkinter as tk
from tkinter import messagebox
import json
import hashlib
from utils.otp_utils import generate_otp
from utils.mail_utils import send_otp_email
from panels.otp_dialog import OTPDialog
from config import USER_DB, log_event

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Đăng nhập", font=("Segoe UI", 14)).pack(pady=10)

        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(pady=5)
        self.pw_entry = tk.Entry(self, width=30, show="*")
        self.pw_entry.pack(pady=5)

        tk.Button(self, text="Đăng nhập", command=self.login).pack(pady=8) # không cần lambda vì không có đối số
        tk.Button(self, text="Chưa có tài khoản?", command=lambda: master.show_frame("RegisterFrame")).pack() # dùng lambda vì phải nhận đối số. Nếu nhập command=master.show_frame("RegisterFrame") python sẽ hiểu thực thi lệnh ngay và trả về giá trị ở phần return của hàm gây lỗi.

    def login(self):
        email = self.email_entry.get().strip() #strip() để loại bỏ các ký tự khoảng trắng
        pw = self.pw_entry.get().strip()

        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        user = users.get(email)
        if not user:
            messagebox.showerror("Lỗi", "Sai email hoặc passphrase!")
            return

        salt = user["salt"]
        pw_salted = pw + salt
        pw_hash = hashlib.sha256(pw_salted.encode()).hexdigest()

        if pw_hash != user["pass_hash"]:
            messagebox.showerror("Lỗi", "Sai email hoặc passphrase!")
            return
        else:
            otp_code = generate_otp(email)
            send_otp_email(email, otp_code)

            messagebox.showinfo("Gửi OTP", "Mã OTP đã được gửi qua email.\nVui lòng kiểm tra hộp thư đến.")
            log_event(f"Gửi OTP cho: {email}, mã: {otp_code}")
            OTPDialog(self, email)