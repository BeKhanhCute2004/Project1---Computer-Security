import tkinter as tk
from tkinter import messagebox
from utils.verify_pass_utils import verify_passphrase

class PassphraseDialog(tk.Toplevel):
    def __init__(self, master, email, callback):
        super().__init__(master)
        self.email = email
        self.callback = callback
        self.title("Xác thực lại passphrase")
        self.geometry("300x150")

        tk.Label(self, text="Vui lòng nhập lại passphrase").pack(pady=10)
        self.passphrase_entry = tk.Entry(self, show="*")
        self.passphrase_entry.pack(pady=5)
        tk.Button(self, text="Xác nhận", command=self.verify).pack(pady=8)

    def verify(self):
        user_input = self.passphrase_entry.get().strip()
        if verify_passphrase(self.email, user_input):
            messagebox.showinfo("Thành công", "Xác thực passphrase thành công!")
            self.destroy()
            self.callback(user_input)  # Gửi passphrase về nơi gọi
        else:
            messagebox.showerror("Thất bại", "Passphrase không đúng.")
            self.destroy()