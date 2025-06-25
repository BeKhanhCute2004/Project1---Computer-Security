import secrets
from datetime import datetime, timedelta

otp_cache = {}
OTP_LENGTH = 6
OTP_LIFETIME_SECONDS = 300

def generate_otp(email: str) -> str:
    code_int = secrets.randbelow(10**OTP_LENGTH)
    code = f"{code_int:0{OTP_LENGTH}d}"
    expiry_time = datetime.now() + timedelta(seconds=OTP_LIFETIME_SECONDS)
    otp_cache[email] = (code, expiry_time)
    return code

def verify_otp(email: str, user_otp: str) -> bool:
    if email not in otp_cache:
        return False
    
    stored_code, expiry_time = otp_cache[email]

    if datetime.now() > expiry_time:
        del otp_cache[email]
        return False
    
    if stored_code == user_otp:
        del otp_cache[email]
        return True
    else:
        return False