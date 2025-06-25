import secrets
from datetime import datetime, timedelta

otp_cache = {}
OTP_LENGTH = 6
OTP_LIFETIME_SECONDS = 300

def generate_otp(email) -> str:
    code_int = secrets.randbelow(10**OTP_LENGTH) # sinh số ngẫu nhiên từ 0 đến 10^OTP_LENGTH - 1
    code = f"{code_int:0{OTP_LENGTH}d}" # định dạng số thành chuỗi với độ dài cố định là OTP_LENGTH ở dạng thập phân, thêm số 0 vào đầu nếu cần (f"{code_int:0{OTP_LENGTH}d}" = f"code_int:06d")
    expiry_time = datetime.now() + timedelta(seconds=OTP_LIFETIME_SECONDS)
    otp_cache[email] = (code, expiry_time)
    return code

def verify_otp(email: str, user_otp: str) -> bool:
    if email not in otp_cache:
        return False
    
    stored_code, expiry_time = otp_cache[email]

    if datetime.now() > expiry_time:
        del otp_cache[email] # Xóa mã OTP đã hết hạn
        return False
    
    if stored_code == user_otp:
        del otp_cache[email] # Xóa mã OTP sau khi xác thực thành công vì OTP chỉ dùng một lần
        return True
    else:
        return False