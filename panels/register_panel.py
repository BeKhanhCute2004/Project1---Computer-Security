import tkinter as tk
from tkinter import ttk, messagebox
import json
import hashlib
import secrets
import datetime
from utils.crypto_utils import generate_rsa_keys
from config import USER_DB, log_event

class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Đăng ký tài khoản", font=("Segoe UI", 14)).pack(pady=10)

        # Khung nhập liệu
        form = tk.Frame(self)
        form.pack()

        self.inputs = {}
        labels = ["Email", "Họ tên", "Địa chỉ", "SĐT", "Passphrase"]

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=4)
            entry = tk.Entry(form, width=30, show="*" if label == "Passphrase" else "")
            entry.grid(row=i, column=1, pady=4)
            self.inputs[label] = entry

        # Thêm chọn ngày sinh
        tk.Label(form, text="Ngày sinh:").grid(row=len(labels), column=0, sticky="e", padx=5, pady=4)
        dob_frame = tk.Frame(form)
        dob_frame.grid(row=len(labels), column=1, pady=4)

        # Combobox ngày 
        self.day_var = tk.StringVar()
        # textvariable là biến liên kết với combobox, khi giá trị thay đổi thì biến này cũng sẽ thay đổi, trạng thái chỉ đọc
        day_cb = ttk.Combobox(dob_frame, textvariable=self.day_var, width=4, values=[str(i) for i in range(1, 32)], state="readonly")
        day_cb.set("1") # Thiết lập giá trị mặc định là ngày 1
        day_cb.pack(side="left")
        tk.Label(dob_frame, text="/").pack(side="left") # Thêm nhãn "/" giữa các combobox

        # Combobox tháng
        self.month_var = tk.StringVar() # StringVar là biến có thể thay đổi giá trị, dùng để lưu trữ giá trị của combobox
        month_cb = ttk.Combobox(dob_frame, textvariable=self.month_var, width=4, values=[str(i) for i in range(1, 13)], state="readonly")
        month_cb.set("1")
        month_cb.pack(side="left")
        tk.Label(dob_frame, text="/").pack(side="left")

        # Combobox năm
        self.year_var = tk.StringVar()
        current_year = datetime.datetime.now().year
        years = [str(y) for y in range(current_year - 100, current_year + 1)]
        year_cb = ttk.Combobox(dob_frame, textvariable=self.year_var, width=6, values=years[::-1], state="readonly")
        year_cb.set(str(current_year - 20)) # Thiết lập giá trị mặc định là 20 tuổi =)))
        year_cb.pack(side="left")

        tk.Button(self, text="Đăng ký", command=self.register).pack(pady=10)
        tk.Button(self, text="← Quay lại đăng nhập", command=lambda: master.show_frame("LoginFrame")).pack()

    def register(self):
        email = self.inputs["Email"].get().strip()
        name = self.inputs["Họ tên"].get().strip()
        address = self.inputs["Địa chỉ"].get().strip()
        phone = self.inputs["SĐT"].get().strip()
        pw = self.inputs["Passphrase"].get().strip()
        day = self.day_var.get()
        month = self.month_var.get()
        year = self.year_var.get()
        dob = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        if not all([email, name, dob, address, phone, pw]):
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
            "dob": dob,
            "address": address,
            "phone": phone,
            "salt": salt,
            "pass_hash": pw_hash
        }

        with open(USER_DB, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False) # ghi users vào f dưới dạng json. indent: thụt 2 space, ensure_ascii: Đảm bảo các ký tự tiếng Việt không bị chuyển thành mã ASCII.

        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        log_event(f"Đăng ký thành công: {email}")
        self.master.show_frame("LoginFrame")
        generate_rsa_keys(email, pw)