import os, json
from base64 import b64encode, b64decode
from datetime import datetime, timedelta
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from config import KEY_FOLDER, PUBLIC_KEY_BOOK, log_event

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
        "salt": b64encode(salt).decode(), # chuyển đổi salt sang base64 sau đó decode sang chuỗi để lưu trữ
        "nonce": b64encode(cipher.nonce).decode(), # nonce dùng để đảm bảo tính ngẫu nhiên của mỗi lần mã hóa
        "tag": b64encode(tag).decode(), # tag dùng để xác thực tính toàn vẹn của dữ liệu
        "ciphertext": b64encode(ciphertext).decode()
    }

    # === Lưu public key và private key đã mã hóa ===
    pub_path = os.path.join(KEY_FOLDER, f"{email}_public.pem")
    priv_path = os.path.join(KEY_FOLDER, f"{email}_private_enc.json")

    with open(pub_path, "wb") as f: # wb để ghi file nhị phân vì public key là dữ liệu nhị phân
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

def reencrypt_private_key(email, old_pass, new_pass):
    # load dữ liệu mã hóa cũ
    with open(f"rsa_keys/{email}_private_enc.json", "r") as f:
        enc = json.load(f)

    # giải mã
    old_key = PBKDF2(old_pass, b64decode(enc["salt"]), dkLen=32, count=100_000)
    cipher = AES.new(old_key, AES.MODE_GCM, nonce=b64decode(enc["nonce"])) # sử dụng nonce để khởi tạo cipher
    private_key = cipher.decrypt_and_verify(b64decode(enc["ciphertext"]), b64decode(enc["tag"]))

    # mã hóa lại với passphrase mới
    new_salt = get_random_bytes(16)
    new_key = PBKDF2(new_pass, new_salt, dkLen=32, count=100_000)
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

def load_private_key(email, passphrase):
    with open(f"{KEY_FOLDER}/{email}_private_enc.json", "r") as f:
        enc = json.load(f)
    salt = b64decode(enc["salt"])
    key = PBKDF2(passphrase, salt, dkLen=32, count=100_000)
    cipher = AES.new(key, AES.MODE_GCM, nonce=b64decode(enc["nonce"]))
    private_key = cipher.decrypt_and_verify(b64decode(enc["ciphertext"]), b64decode(enc["tag"]))
    return RSA.import_key(private_key)

# def encrypt_file(sender_email, recipient_email, file_path, out_folder="encrypted_files"):
#     os.makedirs(out_folder, exist_ok=True)
#     with open(PUBLIC_KEY_BOOK, "r", encoding="utf-8") as f:
#         keybook = json.load(f)
#     if recipient_email not in keybook:
#         return False, "Không tìm thấy public key người nhận."

#     pub_key = RSA.import_key(b64decode(keybook[recipient_email]["public_key"]))
#     ksession = get_random_bytes(32)
#     iv = get_random_bytes(12)
#     cipher_aes = AES.new(ksession, AES.MODE_GCM, nonce=iv)

#     with open(file_path, "rb") as f:
#         data = f.read()
#     ciphertext, tag = cipher_aes.encrypt_and_digest(data)

#     cipher_rsa = PKCS1_OAEP.new(pub_key) # sử dụng OAEP để mã hóa khóa phiên, an toàn hơn so với dùng trực tiếp RSA
#     enc_ksession = cipher_rsa.encrypt(ksession)

#     metadata = {
#         "sender": sender_email,
#         "recipient": recipient_email,
#         "original_filename": os.path.basename(file_path),
#         "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         "enc_ksession": b64encode(enc_ksession).decode(),
#         "aes_iv": b64encode(iv).decode(),
#         "aes_tag": b64encode(tag).decode()
#     }

#     result = {
#         "metadata": metadata,
#         "ciphertext": b64encode(ciphertext).decode()
#     }

#     out_name = os.path.splitext(os.path.basename(file_path))[0] + ".enc"
#     out_path = os.path.join(out_folder, out_name)
#     with open(out_path, "w", encoding="utf-8") as f:
#         json.dump(result, f, indent=2)

#     log_event(f"Đã mã hóa file '{os.path.basename(file_path)}' để gửi cho '{recipient_email}'")

#     return True, out_path

# def decrypt_file(file_path, user_email, passphrase):
#     try:
#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)
#         metadata = data["metadata"]
#         ciphertext = b64decode(data["ciphertext"])

#         rsa_key = load_private_key(user_email, passphrase)
#         cipher_rsa = PKCS1_OAEP.new(rsa_key)
#         ksession = cipher_rsa.decrypt(b64decode(metadata["enc_ksession"]))

#         cipher = AES.new(ksession, AES.MODE_GCM, nonce=b64decode(metadata["aes_iv"]))
#         plaintext = cipher.decrypt_and_verify(ciphertext, b64decode(metadata["aes_tag"]))

#         out_name = "decrypted_" + metadata["original_filename"]
#         with open(out_name, "wb") as f:
#             f.write(plaintext)
#         log_event(f"Đã giải mã file '{os.path.basename(file_path)}' từ '{metadata['sender']}'")

#         return True, out_name, metadata
#     except Exception as e:
#         return False, str(e), None
def encrypt_file(sender_email, recipient_email, file_path, out_folder="encrypted_files"):
    os.makedirs(out_folder, exist_ok=True)

    # Đọc public key người nhận
    with open(PUBLIC_KEY_BOOK, "r", encoding="utf-8") as f:
        keybook = json.load(f)
    if recipient_email not in keybook:
        return False, "Không tìm thấy public key người nhận."

    pub_key = RSA.import_key(b64decode(keybook[recipient_email]["public_key"]))

    # === Tạo khóa phiên AES và mã hóa nó bằng RSA ===
    ksession = get_random_bytes(32)
    cipher_rsa = PKCS1_OAEP.new(pub_key)
    enc_ksession = cipher_rsa.encrypt(ksession)

    file_size = os.path.getsize(file_path)
    block_size = 1024 * 1024  # 1MB

    metadata = {
        "sender": sender_email,
        "recipient": recipient_email,
        "original_filename": os.path.basename(file_path),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "enc_ksession": b64encode(enc_ksession).decode()
    }

    # === Nếu file > 5MB thì chia thành block ===
    if file_size > 5 * 1024 * 1024:
        blocks = []
        block_num = 0
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(block_size)
                if not chunk:
                    break
                block_num += 1
                iv = get_random_bytes(12)
                cipher = AES.new(ksession, AES.MODE_GCM, nonce=iv)
                ciphertext, tag = cipher.encrypt_and_digest(chunk)

                blocks.append({
                    "iv": b64encode(iv).decode(),
                    "tag": b64encode(tag).decode(),
                    "ciphertext": b64encode(ciphertext).decode()
                })
                print(f"Block {block_num}: {len(chunk)} bytes đã được mã hóa.")

        result = {
            "metadata": metadata,
            "blocks": blocks
        }
    else:
        # === Nếu file nhỏ hoặc bằng 5MB thì mã hóa toàn bộ một lần ===
        with open(file_path, "rb") as f:
            file_data = f.read()

        iv = get_random_bytes(12)
        cipher = AES.new(ksession, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(file_data)

        result = {
            "metadata": {
                **metadata,
                "aes_iv": b64encode(iv).decode(),
                "aes_tag": b64encode(tag).decode()
            },
            "ciphertext": b64encode(ciphertext).decode()
        }

    # === Ghi ra file .enc ===
    out_name = os.path.splitext(os.path.basename(file_path))[0] + ".enc"
    out_path = os.path.join(out_folder, out_name)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    log_event(f"Đã mã hóa file '{os.path.basename(file_path)}' để gửi cho '{recipient_email}'")
    return True, out_path

def decrypt_file(file_path, user_email, passphrase):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        metadata = data["metadata"]

        rsa_key = load_private_key(user_email, passphrase)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        ksession = cipher_rsa.decrypt(b64decode(metadata["enc_ksession"]))

        if "blocks" in data:
            # === Giải mã theo block ===
            plaintext = b""
            for i, block in enumerate(data["blocks"], start=1):
                iv = b64decode(block["iv"])
                tag = b64decode(block["tag"])
                ciphertext = b64decode(block["ciphertext"])

                cipher = AES.new(ksession, AES.MODE_GCM, nonce=iv)
                chunk = cipher.decrypt_and_verify(ciphertext, tag)
                plaintext += chunk
                print(f"Block {i}: {len(chunk)} bytes đã được giải mã.")
        else:
            # === Giải mã toàn bộ một lần ===
            iv = b64decode(metadata["aes_iv"])
            tag = b64decode(metadata["aes_tag"])
            ciphertext = b64decode(data["ciphertext"])

            cipher = AES.new(ksession, AES.MODE_GCM, nonce=iv)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        out_name = "decrypted_" + metadata["original_filename"]
        with open(out_name, "wb") as f:
            f.write(plaintext)

        log_event(f"Đã giải mã file '{os.path.basename(file_path)}' từ '{metadata['sender']}'")
        return True, out_name, metadata
    except Exception as e:
        return False, str(e), None
