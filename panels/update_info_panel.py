import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.simpledialog import askstring
import json
import hashlib
import secrets
import datetime
from utils.crypto_utils import reencrypt_private_key
from config import USER_DB, log_event

class UpdateInfoPanel(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.user_email = user_email
        self.inputs = {}

        tk.Label(self, text="Cập nhật thông tin tài khoản", font=("Segoe UI", 14)).pack(pady=10)
        form = tk.Frame(self)
        form.pack()

        fields = ["Họ tên", "Địa chỉ", "SĐT", "Passphrase mới (nếu đổi)"]
        for i, label in enumerate(fields):
            tk.Label(form, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=4)
            entry = tk.Entry(form, width=40, show="*" if "Passphrase" in label else "")
            entry.grid(row=i, column=1, pady=4)
            self.inputs[label] = entry

        # Combobox ngày sinh
        tk.Label(form, text="Ngày sinh").grid(row=len(fields), column=0, sticky="e", padx=5, pady=4)
        dob_frame = tk.Frame(form)
        dob_frame.grid(row=len(fields), column=1, pady=4)

        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        current_year = datetime.datetime.now().year

        # Combobox ngày
        self.day_cb = ttk.Combobox(
            dob_frame, textvariable=self.day_var, width=4,
            values=[str(i) for i in range(1, 32)], state="readonly"
        )
        self.day_cb.pack(side="left")
        tk.Label(dob_frame, text="/").pack(side="left")

        # Combobox tháng
        self.month_cb = ttk.Combobox(
            dob_frame, textvariable=self.month_var, width=4,
            values=[str(i) for i in range(1, 13)], state="readonly"
        )
        self.month_cb.pack(side="left")
        tk.Label(dob_frame, text="/").pack(side="left")

        # Combobox năm
        years = [str(y) for y in range(current_year - 100, current_year + 1)]
        self.year_cb = ttk.Combobox(
            dob_frame, textvariable=self.year_var, width=6,
            values=years[::-1], state="readonly"
        )
        self.year_cb.pack(side="left")

        tk.Button(self, text="Lưu thay đổi", command=self.save_changes).pack(pady=8)
        self.load_existing_info()

    def load_existing_info(self):
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
            data = users[self.user_email]
            self.inputs["Họ tên"].insert(0, data["name"])
            self.inputs["Địa chỉ"].insert(0, data.get("address", ""))
            self.inputs["SĐT"].insert(0, data.get("phone", ""))
            # Tách ngày sinh thành 3 phần
            dob = data.get("dob", "") # "" nếu không có ngày sinh
            if dob and len(dob.split("-")) == 3:
                y, m, d = dob.split("-")
                self.day_var.set(str(int(d)))
                self.month_var.set(str(int(m)))
                self.year_var.set(y)
            else:
                self.day_var.set("1")
                self.month_var.set("1")
                self.year_var.set(str(datetime.datetime.now().year - 20))
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không tải được dữ liệu người dùng: {e}")

    def save_changes(self):
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)

            user = users[self.user_email]
            old_passphrase = askstring("Xác nhận", "Nhập passphrase hiện tại để xác thực:", show="*")

            pw_salted = old_passphrase + user["salt"]
            pw_hash = hashlib.sha256(pw_salted.encode()).hexdigest()
            if pw_hash != user["pass_hash"]:
                messagebox.showerror("Lỗi", "Passphrase không chính xác.")
                return

            # Nếu có passphrase mới
            new_pw = self.inputs["Passphrase mới (nếu đổi)"].get().strip()
            if new_pw:
                reencrypt_private_key(self.user_email, old_passphrase, new_pw)

                new_salt = secrets.token_hex(16)
                new_hash = hashlib.sha256((new_pw + new_salt).encode()).hexdigest()
                user["salt"] = new_salt
                user["pass_hash"] = new_hash
                log_event(f"Đổi passphrase cho: {self.user_email}")

            # cập nhật các trường khác
            user["name"] = self.inputs["Họ tên"].get().strip()
            user["address"] = self.inputs["Địa chỉ"].get().strip()
            user["phone"] = self.inputs["SĐT"].get().strip()
            # Lưu ngày sinh từ combobox
            day = self.day_var.get()
            month = self.month_var.get()
            year = self.year_var.get()
            user["dob"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            with open(USER_DB, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2, ensure_ascii=False)

            messagebox.showinfo("Thành công", "Cập nhật thông tin thành công.")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu thay đổi: {e}")