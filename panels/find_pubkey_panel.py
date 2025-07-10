import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.find_pubkey_utils import find_public_key_by_email  # adjust import path as needed

class FindPublicKeyPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        tk.Label(self, text="Tìm khóa công khai bằng email", font=("Segoe UI", 14)).pack(pady=10)

        self.email_entry = tk.Entry(self, width=40)
        self.email_entry.pack(pady=5)
        self.email_entry.insert(0, "")

        tk.Button(self, text="Tìm khóa công khai", command=self.search).pack(pady=5)

        self.result_frame = tk.Frame(self)
        self.result_frame.pack(pady=10)

        self.qr_label = None  # to show the image

    def search(self):
        # Clear old results
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        email = self.email_entry.get().strip()
        if not email:
            messagebox.showerror("Lỗi", "Vui lòng nhập email.")
            return

        ok, result = find_public_key_by_email(email)
        if not ok:
            messagebox.showerror("Không tìm thấy", result)
            return

        tk.Label(self.result_frame, text=f"Email: {result['email']}", font=("Segoe UI", 12)).pack(anchor="w")
        tk.Label(self.result_frame, text=f"Ngày tạo: {result['created']}").pack(anchor="w")
        tk.Label(self.result_frame, text=f"Hết hạn: {result['expires']}").pack(anchor="w")

        try:
            img = Image.open(result["qr_code_path"])
            img = img.resize((250, 250), Image.NEAREST)
            
            self.qr_img = ImageTk.PhotoImage(img)
            self.qr_label = tk.Label(self.result_frame, image=self.qr_img)
            self.qr_label.pack(pady=5)
            
        except Exception as e:
            tk.Label(self.result_frame, text=f"Lỗi khi tải QR code: {e}").pack()
