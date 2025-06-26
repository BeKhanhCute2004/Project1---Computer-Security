import tkinter as tk
import json
from tkinter import filedialog, simpledialog
from utils.crypto_utils import decrypt_file

class DecryptPanel(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.user_email = user_email

        tk.Label(self, text="Giải mã tập tin đã nhận", font=("Segoe UI", 14)).pack(pady=10)
        tk.Button(self, text="Chọn file .enc", command=self.pick_file).pack(pady=5)
        self.output = tk.Text(self, height=10)
        self.output.pack(pady=5)
        self.file_path = None

    def pick_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Encrypted files", "*.enc")])
        if not self.file_path:
            return
        passphrase = simpledialog.askstring("Passphrase", "Nhập passphrase:", show="*")
        if not passphrase:
            return

        ok, result, meta = decrypt_file(self.file_path, self.user_email, passphrase)
        if ok:
            self.output.insert(tk.END, f"Đã giải mã thành công:\nLưu tại: {result}\n")
            self.output.insert(tk.END, f"Thông tin:\n{json.dumps(meta, indent=2)}\n")
        else:
            self.output.insert(tk.END, f"Lỗi: {result}\n")
