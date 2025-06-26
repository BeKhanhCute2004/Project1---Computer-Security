import tkinter as tk
from panels.key_status_panel import KeyStatusPanel
from panels.qr_panel import QRPanel
from panels.update_info_panel import UpdateInfoPanel
from panels.encrypt_panel import EncryptPanel
from panels.decrypt_panel import DecryptPanel

class DashboardFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        # Menu trái
        menu = tk.Frame(self)
        menu.pack(side="left", fill="y")

        btns = [
            ("Mã hóa", self.show_encrypt),
            ("Giải mã", self.show_decrypt),
            ("Trạng thái khóa", self.show_key_status),
            ("QR Public Key", self.show_qr),
            ("Cập nhật tài khoản", self.show_update_info),
            ("Đăng xuất", self.logout)
        ]


        for text, cmd in btns:
            tk.Button(menu, text=text, width=20, command=cmd).pack(pady=5)

        # Nội dung phải
        self.content = tk.Frame(self)
        self.content.pack(side="right", expand=True, fill="both")

        self.encrypt_panel = None
        self.decrypt_panel = None
        self.update_info_panel = None
        self.key_status_panel = None
        self.qr_panel = None
        self.update_key_status_panel(self.master.current_user)


        # Mặc định hiện panel khóa
        self.show_key_status()

    def update_key_status_panel(self, user_email):
        # Xóa toàn bộ nội dung cũ trước khi tạo panel mới
        self.clear_content()
        self.key_status_panel = KeyStatusPanel(self.content, user_email=user_email)
        self.key_status_panel.pack(fill="both", expand=True)
    
    def show_encrypt(self):
        self.clear_content()
        if self.encrypt_panel:
            self.encrypt_panel.destroy()
        self.encrypt_panel = EncryptPanel(self.content, self.master.current_user)
        self.encrypt_panel.pack(fill="both", expand=True)

    def show_decrypt(self):
        self.clear_content()
        if self.decrypt_panel:
            self.decrypt_panel.destroy()
        self.decrypt_panel = DecryptPanel(self.content, self.master.current_user)
        self.decrypt_panel.pack(fill="both", expand=True)

    def show_key_status(self):
        self.clear_content()
        self.update_key_status_panel(self.master.current_user)
        self.key_status_panel.tkraise()

    def show_qr(self):
        self.clear_content()

        # Nếu panel chưa có hoặc email đổi thì tạo mới
        if self.qr_panel:
            self.qr_panel.destroy()

        self.qr_panel = QRPanel(self.content, user_email=self.master.current_user)
        self.qr_panel.pack(fill="both", expand=True)

    def show_update_info(self):
        self.clear_content()
        if self.update_info_panel:
            self.update_info_panel.destroy()
        self.update_info_panel = UpdateInfoPanel(self.content, user_email=self.master.current_user)
        self.update_info_panel.pack(fill="both", expand=True)

    def clear_content(self):
        # Xóa nội dung bên phải
        for widget in self.content.winfo_children(): 
            widget.destroy()

    def logout(self):
        self.clear_content()
        # Đặt lại user hiện tại và quay về màn hình đăng nhập
        self.master.current_user = None
        self.master.show_frame("LoginFrame")