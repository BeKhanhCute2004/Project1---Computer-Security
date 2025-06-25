import tkinter as tk
import json
import tkinter as tk
from tkinter import messagebox
import hashlib
import secrets
import datetime
import os
from mail_utils import send_otp_email
from otp_utils import generate_otp, verify_otp
from crypto_utils import generate_rsa_keys

USER_DB = "users.json"

# Hàm ghi log sự kiện vào file log.txt
def log_event(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("An ninh máy tính - Demo")
        self.geometry("500x500")
        self.current_user = None
        self.frames = {}

        for F in (LoginFrame, RegisterFrame, DashboardFrame):
            frame = F(self)
            self.frames[F.__name__] = frame # __name__ hiển thị tên class hiện tại, thuộc tính có sẵn trong class
            frame.grid(row=0, column=0, sticky="nsew") # kéo frame full khung hình bắt đầu từ dòng 0 cột 0

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise() # đặt frame lên trên cùng của app


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
            OTPDialog(self, email)
            log_event(f"Gửi OTP cho: {email}, mã: {otp_code}")
        

class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Đăng ký tài khoản", font=("Segoe UI", 14)).pack(pady=10)

        # Khung nhập liệu
        form = tk.Frame(self)
        form.pack()

        self.inputs = {}
        labels = ["Email", "Họ tên", "Passphrase"]

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=4) # đặt các nhãn vào lưới, sticky east kéo nhãn đến hết bên phải
            entry = tk.Entry(form, width=30, show="*" if label == "Passphrase" else "") # tạo ô nhập liệu
            entry.grid(row=i, column=1, pady=4) # gán vào cột 2 cùng dòng với các nhãn
            self.inputs[label] = entry

        tk.Button(self, text="Đăng ký", command=self.register).pack(pady=10)
        tk.Button(self, text="← Quay lại đăng nhập", command=lambda: master.show_frame("LoginFrame")).pack()

    def register(self):
        email = self.inputs["Email"].get().strip()
        name = self.inputs["Họ tên"].get().strip()
        pw = self.inputs["Passphrase"].get().strip()

        if not email or not name or not pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin.")
            return

        # Lưu vào file JSON
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if email in users:
            messagebox.showerror("Trùng email", "Email này đã được đăng ký.")
            return

        salt = secrets.token_hex(16)  # 16 bytes = 32 ký tự hex, không dùng random vì không đủ an toàn, có thể đoán được seed.
        pw_salted = pw + salt
        pw_hash = hashlib.sha256(pw_salted.encode()).hexdigest() # Mã hóa mật khẩu bằng SHA-256, encode() chuyển chuỗi thành bytes sử dụng bảng mã mặc định utf8, hexdigest() chuyển kết quả thành chuỗi hex 64 ký tự.
        # Lưu thông tin người dùng vào từ điển
        users[email] = {
            "name": name,
            "salt": salt,
            "pass_hash": pw_hash
        }

        with open(USER_DB, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False) # ghi users vào f dưới dạng json. indent: thụt 2 space, ensure_ascii: Đảm bảo các ký tự tiếng Việt không bị chuyển thành mã ASCII.

        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        log_event(f"Đăng ký thành công: {email}")
        self.master.show_frame("LoginFrame")
        generate_rsa_keys(email, pw)

class OTPDialog(tk.Toplevel): # Toplevel tạo cửa sổ con độc lập với cửa sổ chính, pop up khi cần xác thực OTP.
    def __init__(self, master, email):
        super().__init__(master)
        self.email = email
        self.title("Xác thực OTP")
        self.geometry("300x150")

        tk.Label(self, text="Nhập mã OTP đã gửi đến email").pack(pady=10)
        self.otp_entry = tk.Entry(self)
        self.otp_entry.pack(pady=5)
        tk.Button(self, text="Xác nhận", command=self.verify).pack(pady=8)

    def verify(self):
        user_input = self.otp_entry.get().strip()
        if verify_otp(self.email, user_input):
            tk.messagebox.showinfo("Thành công", "Xác thực OTP thành công!")
            self.destroy()

            # Gán current_user
            self.master.master.current_user = self.email
            # Tạo lại KeyStatusPanel với user mới
            self.master.master.frames["DashboardFrame"].update_key_status_panel(self.email)
            # Chuyển sang dashboard
            self.master.master.show_frame("DashboardFrame")
        else:
            tk.messagebox.showerror("Thất bại", "OTP sai hoặc đã hết hạn.")
            self.destroy()

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

        tk.Button(self, text="Làm mới", command=self.load_info).pack(pady=6)
        self.load_info()

    def load_info(self):
        self.output.delete(1.0, tk.END) # xoá mọi thứ từ dòng 1 cột 0 đến hết (END) trong text widget
        path = f"rsa_keys/{self.user_email}_info.json"
        if not os.path.exists(path):
            self.output.insert(tk.END, "Không tìm thấy thông tin khóa.")
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        lines = [
            f"Email: {data['email']}",
            f"Ngày tạo: {data['created']}",
            f"Hết hạn: {data['expires']}",
            f"Public Key: {data['public_key_file']}",
            f"Private Key (mã hóa): {data['private_key_file']}"
        ]
        self.output.insert(tk.END, "\n".join(lines)) # chèn vào cuối nội dung hiện có, join tất cả chuỗi trong danh sách lines thành một chuỗi duy nhất, ngăn cách bằng ký tự xuống dòng

class DashboardFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Menu trái
        menu = tk.Frame(self)
        menu.pack(side="left", fill="y")

        btns = [
            ("Mã hóa", self.show_encrypt),
            ("Giải mã", self.show_decrypt),
            ("Trạng thái khóa", self.show_key_status),
            ("Đăng xuất", self.logout)
        ]

        for text, cmd in btns:
            tk.Button(menu, text=text, width=20, command=cmd).pack(pady=5)

        # Nội dung phải
        self.content = tk.Frame(self)
        self.content.pack(side="right", expand=True, fill="both")

        self.key_status_panel = None
        self.update_key_status_panel(self.master.current_user)

        # Mặc định hiện panel khóa
        self.show_key_status()

    def update_key_status_panel(self, user_email):
        # Xóa panel cũ nếu có
        if self.key_status_panel:
            self.key_status_panel.destroy()
        self.key_status_panel = KeyStatusPanel(self.content, user_email=user_email)
        self.key_status_panel.pack(fill="both", expand=True)

    def show_encrypt(self):
        self.clear_content()
        tk.Label(self.content, text="🔒 Mã hóa (chưa làm)", font=("Segoe UI", 14)).pack(pady=20)

    def show_decrypt(self):
        self.clear_content()
        tk.Label(self.content, text="🔓 Giải mã (chưa làm)", font=("Segoe UI", 14)).pack(pady=20)

    def show_key_status(self):
        self.clear_content()
        self.update_key_status_panel(self.master.current_user)
        self.key_status_panel.tkraise()

    def clear_content(self):
        # Xóa nội dung bên phải
        for widget in self.content.winfo_children(): 
            widget.destroy()

    def logout(self):
        # Đặt lại user hiện tại và quay về màn hình đăng nhập
        self.master.current_user = None
        self.master.show_frame("LoginFrame")

if __name__ == "__main__":
    app = App()
    app.mainloop()
