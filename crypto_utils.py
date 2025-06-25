from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from base64 import b64encode, b64decode 
import json
import os
from datetime import datetime, timedelta

KEY_FOLDER = "rsa_keys"
os.makedirs(KEY_FOLDER, exist_ok=True)

def generate_rsa_keys(email: str, passphrase: str):
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key() 

    # === Mã hóa private key bằng AES ===
    salt = get_random_bytes(16)
    aes_key = PBKDF2(passphrase, salt, dkLen=32, count=100_000)  # sinh key từ pass và salt trộn 100.000 lần

    cipher = AES.new(aes_key, AES.MODE_GCM) # sử dụng chế độ GCM để mã hóa
    ciphertext, tag = cipher.encrypt_and_digest(private_key)

    encrypted_data = {
        "salt": b64encode(salt).decode(), 
        "nonce": b64encode(cipher.nonce).decode(), # nonce dùng để đảm bảo tính ngẫu nhiên của mỗi lần mã hóa
        "tag": b64encode(tag).decode(), # tag dùng để xác thực tính toàn vẹn của dữ liệu
        "ciphertext": b64encode(ciphertext).decode()
    }

    # === Lưu public key và private key đã mã hóa ===
    pub_path = os.path.join(KEY_FOLDER, f"{email}_public.pem")
    priv_path = os.path.join(KEY_FOLDER, f"{email}_private_enc.json")

    with open(pub_path, "wb") as f:
        f.write(public_key)

    with open(priv_path, "w", encoding="utf-8") as f:
        json.dump(encrypted_data, f, indent=2)

    # === Lưu trạng thái khóa ===
    info = {
        "email": email,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires": (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d"),
        "public_key_file": pub_path,
        "private_key_file": priv_path
    }

    with open(os.path.join(KEY_FOLDER, f"{email}_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)

    return True