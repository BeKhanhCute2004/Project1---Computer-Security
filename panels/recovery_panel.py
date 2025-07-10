import tkinter as tk
from tkinter import messagebox, Tk

from utils.recovery_utils import recover_account

class RecoveryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Khôi phục tài khoản", font=("Segoe UI", 14)).pack(pady=10)

        self.controller = controller

        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "")

        self.recovery_code_entry = tk.Entry(self, width=40)
        self.recovery_code_entry.insert(0, "Mã khôi phục")
        self.recovery_code_entry.pack(pady=5)

        self.new_passphrase_entry = tk.Entry(self, width=40, show="*")
        self.new_passphrase_entry.insert(0, "")
        self.new_passphrase_entry.pack(pady=5)

        tk.Button(self, text="Khôi phục", command=self.recover).pack(pady=8)
        tk.Button(self, text="Quay lại đăng nhập", command=lambda: controller.show_frame("LoginFrame")).pack()

    def recover(self):
        email = self.email_entry.get().strip()
        code = self.recovery_code_entry.get().strip()
        new_pass = self.new_passphrase_entry.get().strip()
        
        if not all([email, code, new_pass]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ.")
            return

        success, msg = recover_account(email, code, new_pass)
        if success:
            messagebox.showinfo("Thành công", msg)
            self.controller.show_frame("LoginFrame")
        else:
            messagebox.showerror("Lỗi", msg)
        