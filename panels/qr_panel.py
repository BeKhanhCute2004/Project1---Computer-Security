import tkinter as tk
from tkinter import filedialog
import json
from utils.qr_utils import generate_qr_for_public_key, read_qr_from_image, save_public_key_entry

class QRPanel(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.user_email = user_email
        tk.Label(self, text="Mã QR Public Key", font=("Segoe UI", 14)).pack(pady=10)

        tk.Button(self, text="Tạo mã QR cho public key", command=self.create_qr).pack(pady=5)
        tk.Button(self, text="Đọc mã QR từ ảnh", command=self.read_qr).pack(pady=5)

        self.output = tk.Text(self, width=70, height=15, wrap="word")
        self.output.pack(padx=10, pady=5)

    def create_qr(self):
        ok, result = generate_qr_for_public_key(self.user_email)
        if ok:
            self.output.insert(tk.END, f"Đã tạo QR: {result}\n")
        else:
            self.output.insert(tk.END, f"Lỗi: {result}\n")

    def read_qr(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not file_path:
            return
        ok, data = read_qr_from_image(file_path)
        if ok:
            save_public_key_entry(data)
            self.output.insert(tk.END, f"Đã đọc QR và lưu public key:\n{json.dumps(data, indent=2)}\n")
        else:
            self.output.insert(tk.END, f"Lỗi đọc QR: {data}\n")
