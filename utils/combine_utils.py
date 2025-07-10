import os
import json
from base64 import b64encode, b64decode
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from config import KEY_FOLDER
from utils.crypto_utils import load_private_key

def encrypt_separate(sender_email, recipient_email, file_path, out_folder="encrypted_files"):
    try:
        # Tải khóa công khai của người nhận
        with open(f"{KEY_FOLDER}/{recipient_email}_public.pem", "rb") as f:
            recipient_key = RSA.import_key(f.read())

        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        ksession = get_random_bytes(32)

        # Mã hóa file
        with open(file_path, "rb") as f:
            plaintext = f.read()

        cipher_aes = AES.new(ksession, AES.MODE_GCM)
        ciphertext, tag = cipher_aes.encrypt_and_digest(plaintext)

        # Mã hóa khóa phiên bằng RSA
        enc_ksession = cipher_rsa.encrypt(ksession)
    
        data = {
            "type": "separate",
            "metadata": {
                "sender": sender_email,
                "recipient": recipient_email,
                "original_filename": os.path.basename(file_path),
                "aes_tag": b64encode(tag).decode(),
                "aes_iv": b64encode(cipher_aes.nonce).decode()
            },
            "ciphertext": b64encode(ciphertext).decode()
        }
        name = os.path.splitext(os.path.basename(file_path))[0]
        enc_name = name + "_separate.enc"
        enc_path = os.path.join(out_folder, enc_name)
        with open(enc_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        key = {
            "enc_ksession": b64encode(enc_ksession).decode()
        }
        key_file_name = name + ".key"
        key_file_path = os.path.join(out_folder, key_file_name)

        with open(key_file_path, "w", encoding="utf-8") as f:
            json.dump(key, f, indent=2)
        return True, (enc_path, key_file_path)
    
    except Exception as e:
        return False, str(e)

def decrypt_auto_detect(file_path, user_email, passphrase):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "type" in data and data["type"] == "separate":
            base = file_path.rsplit("_separate.enc", 1)[0]
            key_file = base + ".key"
            with open(key_file, "r", encoding="utf-8") as f:
                key_data = json.load(f)
            enc_ksession = b64decode(key_data["enc_ksession"])
            metadata = data["metadata"]
            ciphertext = b64decode(data["ciphertext"])
        elif "metadata" in data and "ciphertext" in data:
            metadata = data["metadata"]
            enc_ksession = b64decode(data["metadata"]["enc_ksession"])
            ciphertext = b64decode(data["ciphertext"])
        else:
            return False, "Định dạng file không hợp lệ."

        private_key = load_private_key(user_email, passphrase)
        cipher_rsa = PKCS1_OAEP.new(private_key)
        ksession = cipher_rsa.decrypt(enc_ksession)

        cipher = AES.new(ksession, AES.MODE_GCM, nonce=b64decode(metadata["aes_iv"]))
        plaintext = cipher.decrypt_and_verify(ciphertext, b64decode(metadata["aes_tag"]))

        out_file = "decrypted_" + metadata["original_filename"]
        with open(out_file, "wb") as f:
            f.write(plaintext)

        return True, out_file, metadata
    except Exception as e:
        return False, str(e), None
