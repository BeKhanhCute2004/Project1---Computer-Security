import json
import secrets
import hashlib
import os
from base64 import b64decode, b64encode
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from config import USER_DB, KEY_FOLDER
from utils.crypto_utils import load_private_key

# Sinh mã khôi phục ngẫu nhiên
def generate_recovery_code():    
    return secrets.token_urlsafe(16)

# Băm mã khôi phục bằng SHA-256
def hash_recovery_code(code):    
    return hashlib.sha256(code.encode()).hexdigest()

# Mã hóa private key bằng recovery code, ghi ra file riêng.
# Chỉ gọi hàm này khi user kích hoạt khôi phục tài khoản.
def encrypt_private_key_by_recovery(email, private_key_bytes, recovery_code):
    salt = get_random_bytes(16)
    key = PBKDF2(recovery_code, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(private_key_bytes)

    enc = {
        "salt": b64encode(salt).decode(),
        "nonce": b64encode(cipher.nonce).decode(),
        "tag": b64encode(tag).decode(),
        "ciphertext": b64encode(ciphertext).decode()
    }

    file_path = os.path.join(KEY_FOLDER, f"{email}_private_enc_recovery.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(enc, f, indent=2)

def decrypt_private_key_in_recovery(email, recovery_code):
    path = f"{KEY_FOLDER}/{email}_private_enc_recovery.json"
    # print(f"Đang đọc file: {path}")
    with open(path, "r", encoding="utf-8") as f:
        enc = json.load(f)
    try: 
        # print("Nội dung file backup:")
        # for k in ("salt", "nonce", "tag", "ciphertext"):
        #     print(f"   - {k}: {enc.get(k, 'thiếu')}")
        salt = b64decode(enc["salt"])
        nonce = b64decode(enc["nonce"])
        tag = b64decode(enc["tag"])
        ciphertext = b64decode(enc["ciphertext"])
    
        key = PBKDF2(recovery_code, salt, dkLen=32, count=100_000)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        private_key = cipher.decrypt_and_verify(ciphertext, tag)
        return private_key
    except Exception as e:
        # print(f"Giải mã thất bại: {e}")
        raise Exception(f"Lỗi giải mã bằng mã khôi phục: {e}")

def reencrypt_private_key(email, new_passphrase, private_key):
    # Mã hóa lại với passphrase mới
    new_salt = get_random_bytes(16)
    new_key = PBKDF2(new_passphrase, new_salt, dkLen=32, count=100_000)
    new_cipher = AES.new(new_key, AES.MODE_GCM)
    new_ciphertext, new_tag = new_cipher.encrypt_and_digest(private_key)

    new_enc = {
        "salt": b64encode(new_salt).decode(),
        "nonce": b64encode(new_cipher.nonce).decode(),
        "tag": b64encode(new_tag).decode(),
        "ciphertext": b64encode(new_ciphertext).decode()
    }

    with open(f"rsa_keys/{email}_private_enc.json", "w") as f:
        json.dump(new_enc, f, indent=2)

def recover_account(email, recovery_code, new_passphrase):
    # Khôi phục tài khoản bằng mã khôi phục, cập nhật passphrase mới
    try:
        with open(USER_DB, "r", encoding="utf-8") as f:
            users = json.load(f)
    except FileNotFoundError:
        return False, "Không tìm thấy cơ sở dữ liệu người dùng."

    user = users.get(email)
    if not user:
        return False, "Email không tồn tại."

    stored_hash = user.get("recovery_code_hash")
    if not stored_hash:
        return False, "Tài khoản này không có hoặc đã dùng mã khôi phục."

    input_hash = hash_recovery_code(recovery_code)
    if input_hash != stored_hash:
        return False, "Mã khôi phục không đúng."

    # Bắt đầu giải mã khóa cũ và mã hóa lại bằng passphrase mới
    try:
        private_key = decrypt_private_key_in_recovery(email, recovery_code)  # Đảm bảo hàm này đọc _recovery.json
        if not isinstance(private_key, bytes):
            return False, "Lỗi: private key không hợp lệ."
        reencrypt_private_key(email, new_passphrase, private_key)
    except Exception as e:
        return False, f"{e}"


    # Cập nhật pass_hash mới
    salted = new_passphrase + user["salt"]
    user["pass_hash"] = hashlib.sha256(salted.encode()).hexdigest()

    # Xóa mã khôi phục sau khi dùng
    user.pop("recovery_code_hash", None)

    # Ghi lại file
    users[email] = user
    with open(USER_DB, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

    # print("Email nhập:", email)
    # print("Recovery code nhập:", recovery_code)
    # print("Hash recovery code nhập:", hash_recovery_code(recovery_code))
    # print("Hash recovery code đã lưu:", user.get("recovery_code_hash"))
    return True, "Khôi phục tài khoản và đổi passphrase thành công!"

def create_recovery_encrypted_key(email: str, passphrase: str, recovery_code: str):
    """
    Sau khi đã tạo khóa chính, hàm này tạo bản mã hóa riêng bằng recovery code.
    """
    try:
        # Tải private key từ bản mã hóa bằng passphrase
        private_key = load_private_key(email, passphrase)
        private_key_bytes = private_key.export_key()
    except Exception as e:
        print(f"Không thể load khóa riêng: {e}")
        return False, f"Lỗi giải mã khóa riêng bằng passphrase: {e}"

    try:
        # Mã hóa lại khóa riêng bằng recovery code
        encrypt_private_key_by_recovery(email, private_key_bytes, recovery_code)
    except Exception as e:
        return False, f"Lỗi mã hóa bằng recovery code: {e}"

    return True, "Đã mã hóa khóa riêng bằng recovery code thành công."
