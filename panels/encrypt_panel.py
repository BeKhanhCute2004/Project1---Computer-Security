import tkinter as tk
from tkinter import filedialog
from utils.crypto_utils import encrypt_file

class EncryptPanel(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.user_email = user_email
        self.file_path = None

        tk.Label(self, text="Mã hóa và gửi tập tin", font=("Segoe UI", 14)).pack(pady=10)

        form = tk.Frame(self)
        form.pack()
        tk.Label(form, text="Email người nhận:").grid(row=0, column=0)
        self.recipient_entry = tk.Entry(form, width=40)
        self.recipient_entry.grid(row=0, column=1)

        tk.Button(self, text="Chọn tập tin", command=self.pick_file).pack(pady=5)
        tk.Button(self, text="Mã hóa", command=self.encrypt_file).pack()

        self.output = tk.Text(self, height=8)
        self.output.pack(pady=5)

    def pick_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.output.insert(tk.END, f"Đã chọn: {self.file_path}\n")

    def encrypt_file(self):
        recipient = self.recipient_entry.get().strip()
        if not recipient or not self.file_path:
            self.output.insert(tk.END, "Thiếu email hoặc file.\n")
            return

        ok, result = encrypt_file(self.user_email, recipient, self.file_path)
        if ok:
            self.output.insert(tk.END, f"Đã mã hóa và lưu tại: {result}\n")
        else:
            self.output.insert(tk.END, f"Lỗi: {result}\n")
