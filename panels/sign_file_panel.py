import tkinter as tk
import os, json
from base64 import b64encode
from datetime import datetime
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from utils.crypto_utils import load_private_key
from config import log_event
from panels.passphrase_dialog import PassphraseDialog
from tkinter import filedialog

class SignFilePanel(tk.Frame):
    def __init__(self, parent, user_email):
        super().__init__(parent)
        self.user_email = user_email
        self.file_path = None

        tk.Label(self, text="Ký số tập tin", font=("Segoe UI", 14)).pack(pady=10)

        tk.Button(self, text="Chọn tập tin", command=self.pick_file).pack(pady=5)
        tk.Button(self, text="Ký số tập tin", command=self.sign_file).pack()

        self.output = tk.Text(self, height=8)
        self.output.pack(pady=5)

    def pick_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.output.insert(tk.END, f"Đã chọn: {self.file_path}\n")

    def sign_file(self):
        if not self.file_path:
            self.output.insert(tk.END, "Chưa chọn tập tin.\n")
            return
        PassphraseDialog(self, self.user_email, self.after_passphrase)

    def after_passphrase(self, passphrase):
        try:
            with open(self.file_path, "rb") as f:
                file_data = f.read()

            file_hash = SHA256.new(file_data)

            # Giải mã private key bằng passphrase
            private_key = load_private_key(self.user_email, passphrase)

            # Ký file sau khi mã hóa bằng private key với chuẩn PKCS#1 v1.5
            signature = pkcs1_15.new(private_key).sign(file_hash)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            sig_data = {
                "file": os.path.basename(self.file_path),
                "signer": self.user_email,
                "timestamp": timestamp,
                "signature": b64encode(signature).decode()
            }

            out_folder = "signatures"
            os.makedirs(out_folder, exist_ok=True)
            base_name, _ = os.path.splitext(os.path.basename(self.file_path))
            sig_filename = base_name + ".sig"
            out_path = os.path.join(out_folder, sig_filename)

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(sig_data, f, indent=2)

            log_event(f"Ký số tập tin '{os.path.basename(self.file_path)}'thành công bởi '{self.user_email}' vào lúc {timestamp}.")

            self.output.insert(tk.END, f"Đã ký số thành công:{out_path}\n")

        except Exception as e:
            self.output.insert(tk.END, f"Lỗi khi ký số:\n{str(e)}\n")
