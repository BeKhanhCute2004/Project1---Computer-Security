import os
import json
from config import KEY_FOLDER
def find_public_key_by_email(email):
    
    img_path = f"{KEY_FOLDER}/{email}_qrcode.png"
    file_path = f"{KEY_FOLDER}/{email}_info.json"
    
    if not os.path.exists(img_path):
        return False, "QR code file not found"
    if not os.path.exists(file_path):
        return False, "Email is not register"
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, {
            "email": data["email"],
            "created": data["created"],
            "expires": data["expires"],
            "qr_code_path": img_path
        }

    except Exception as e:
        return False, f"Error reading user info: {e}"



