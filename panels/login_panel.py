import tkinter as tk
from tkinter import messagebox
import json
import hashlib
from datetime import datetime, timedelta
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

        tk.Button(self, text="Đăng nhập", command=self.login).pack(pady=5) # không cần lambda vì không có đối số
        tk.Button(self, text="Chưa có tài khoản?", command=lambda: master.show_frame("RegisterFrame")).pack(pady=5) # dùng lambda vì phải nhận đối số. Nếu nhập command=master.show_frame("RegisterFrame") python sẽ hiểu thực thi lệnh ngay và trả về giá trị ở phần return của hàm gây lỗi.
        # tk.Button(self, text="Quen mat khau?", command=lambda: master.show_frame("recoveryPanel")).pack()
        tk.Button(self, text="Quên mật khẩu?", command=lambda: master.show_frame("RecoveryFrame")).pack(pady=5)


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
            messagebox.showerror("Lỗi", "Sai email")
            return

        now = datetime.now()

        # Kiểm tra khóa tài khoản
        if user["lock_until"]:
            lock_time = datetime.strptime(user["lock_until"], "%Y-%m-%d %H:%M:%S")
            if now < lock_time:
                wait_secs = int((lock_time - now).total_seconds())
                wait_str = f"{wait_secs // 60} phút {wait_secs % 60} giây"
                messagebox.showerror("Bị khóa", f"Tài khoản đang bị khóa. Vui lòng thử lại sau {wait_str}.")
                return
            else:
                # Reset nếu đã hết khóa
                user["failed_attempts"] = 0
                user["lock_until"] = None

                with open(USER_DB, "w", encoding="utf8") as f:
                    json.dump(users, f, indent=2)


        salt = user["salt"]
        pw_salted = pw + salt
        pw_hash = hashlib.sha256(pw_salted.encode()).hexdigest()

        if pw_hash != user["pass_hash"]:
            # Tăng số lần sai
            user["failed_attempts"] = user.get("failed_attempts", 0) + 1
            log_event(f"Sai mật khẩu cho {email}, lần thứ {user['failed_attempts']}")

            # Nếu sai quá 5 lần, khóa 5 phút
            if user["failed_attempts"] >= 5:
                lock_until = now + timedelta(minutes=5)
                user["lock_until"] = lock_until.strftime("%Y-%m-%d %H:%M:%S")
                messagebox.showerror("Bị khóa", "Bạn đã nhập sai 5 lần. Tài khoản bị khóa trong 5 phút.")
                log_event(f"Đã sai mật khẩu 5 lần, khóa đến lúc: {lock_until.strftime("%Y-%m-%d %H:%M:%S")}")
            else:
                messagebox.showerror("Lỗi", f"Sai passphrase! (Lần {user['failed_attempts']} trên 5)")

            # Cập nhật file
            with open(USER_DB, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)

            return
        else:
            otp_code = generate_otp(email)
            send_otp_email(email, otp_code)

            messagebox.showinfo("Gửi OTP", "Mã OTP đã được gửi qua email.\nVui lòng kiểm tra hộp thư đến.")
            log_event(f"Gửi OTP cho: {email}, mã: {otp_code}")
            OTPDialog(self, email)


