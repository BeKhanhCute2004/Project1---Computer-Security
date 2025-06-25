import smtplib
from email.message import EmailMessage
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

SENDER_EMAIL = os.environ.get("GMAIL_USER")
SENDER_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

if not SENDER_EMAIL or not SENDER_APP_PASSWORD:
    print("Lỗi: Vui lòng thiết lập biến môi trường GMAIL_USER và GMAIL_APP_PASSWORD.")

def send_otp_email(receiver_email, otp_code):
    msg = EmailMessage()
    msg["Subject"] = "Mã OTP xác thực đăng nhập"
    msg["From"] = SENDER_EMAIL 
    msg["To"] = receiver_email

    msg.set_content(f"""
Xin chào,

Mã OTP của bạn là: {otp_code}
Thời gian tạo: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Mã sẽ hết hạn sau 5 phút.

-- Hệ thống bảo mật
""")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_APP_PASSWORD) 
            smtp.send_message(msg)
            print("Đã gửi OTP đến email:", receiver_email)
    except Exception as e:
        print("Gửi OTP thất bại:", e)
