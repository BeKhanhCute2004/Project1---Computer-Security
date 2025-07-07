import tkinter as tk
import os, json
import base64
from config import PUBLIC_KEY_BOOK, log_event
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from tkinter import filedialog

class VerifySignaturePanel(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        self.master = master
        self.user_email = user_email
        self.original_file_path = None
        self.file_path = None

        tk.Label(self, text="Xác minh chữ ký", font=("Segoe UI", 14)).pack(pady=10)

        tk.Button(self, text="Chọn file gốc", command=self.pick_original_file).pack(pady=5)
        tk.Button(self, text="Chọn file chữ ký", command=self.pick_file).pack(pady=5)
        tk.Button(self, text="Xác minh", command=self.verify_signature).pack()

        self.output = tk.Text(self, height=10)
        self.output.pack(pady=5)

    def pick_original_file(self):
        self.original_file_path = filedialog.askopenfilename()
        if self.original_file_path:
            self.output.insert(tk.END, f"Đã chọn file gốc: {self.original_file_path}\n")

    def pick_file(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            self.output.insert(tk.END, f"Đã chọn: {self.file_path}\n")

    def verify_signature(self):
        if not self.original_file_path:
            self.output.insert(tk.END, "Vui lòng chọn file gốc trước khi xác minh.\n")
            return
        
        if not self.file_path:
            self.output.insert(tk.END, "Chưa chọn tập tin chữ ký.\n")
            return

        try:
            # Đọc file chữ ký (.sig)
            with open(self.file_path, "r", encoding="utf-8") as f:
                sig_data = json.load(f)

            # Lấy thông tin từ chữ ký
            filename = sig_data.get("file")
            signature_b64 = sig_data.get("signature")
            timestamp = sig_data.get("timestamp")

            if not filename or not signature_b64 or os.path.basename(self.original_file_path) != filename:
                self.output.insert(tk.END, "File .sig không hợp lệ.\n")
                return

            if not os.path.exists(self.original_file_path):
                self.output.insert(tk.END, f"Không tìm thấy file gốc: {self.original_file_path}\n")
                return

            # Băm lại nội dung file gốc
            with open(self.original_file_path, "rb") as f:
                file_data = f.read()
            file_hash = SHA256.new(file_data)

            # Đọc danh sách public key đã lưu
            with open(PUBLIC_KEY_BOOK, "r", encoding="utf-8") as f:
                keybook = json.load(f)

            found = False
            for email, key_info in keybook.items():
                try:
                    public_key_data = base64.b64decode(key_info["public_key"])
                    public_key = RSA.import_key(public_key_data)
                    signature = base64.b64decode(signature_b64)

                    # Thử xác minh
                    pkcs1_15.new(public_key).verify(file_hash, signature)

                    # Nếu không lỗi → chữ ký đúng
                    self.output.insert(tk.END, f"Chữ ký HỢP LỆ.\n")
                    self.output.insert(tk.END, f"Người ký: {email}\n")
                    self.output.insert(tk.END, f"Thời gian ký: {timestamp}\n")

                    log_event(f"Xác minh chữ ký file '{filename}' thành công - người ký: {email}, thời gian ký: {timestamp}.")
                    found = True
                    break
                except (ValueError, TypeError):
                    continue  # thử key khác

            if not found:
                self.output.insert(tk.END, "Không xác minh được chữ ký với bất kỳ public key nào.\n")
                log_event(f"Xác minh chữ ký file '{filename}' thất bại.")

        except Exception as e:
            self.output.insert(tk.END, f"Lỗi xử lý: {str(e)}\n")
