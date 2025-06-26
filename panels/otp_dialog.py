import tkinter as tk
from utils.otp_utils import verify_otp

class OTPDialog(tk.Toplevel): # Toplevel tạo cửa sổ con độc lập với cửa sổ chính, pop up khi cần xác thực OTP.
    def __init__(self, master, email):
        super().__init__(master)
        self.email = email
        self.title("Xác thực OTP")
        self.geometry("300x150")

        tk.Label(self, text="Nhập mã OTP đã gửi đến email").pack(pady=10)
        self.otp_entry = tk.Entry(self)
        self.otp_entry.pack(pady=5)
        tk.Button(self, text="Xác nhận", command=self.verify).pack(pady=8)

    def verify(self):
        user_input = self.otp_entry.get().strip()
        if verify_otp(self.email, user_input):
            tk.messagebox.showinfo("Thành công", "Xác thực OTP thành công!")
            self.destroy()

            # Gán current_user
            self.master.master.current_user = self.email
            # Tạo lại KeyStatusPanel với user mới
            self.master.master.frames["DashboardFrame"].update_key_status_panel(self.email)
            # Chuyển sang dashboard
            self.master.master.show_frame("DashboardFrame")
        else:
            tk.messagebox.showerror("Thất bại", "OTP sai hoặc đã hết hạn.")
            self.destroy()