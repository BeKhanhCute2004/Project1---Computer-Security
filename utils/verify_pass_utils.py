from config import USER_DB
import json
import hashlib

def verify_passphrase(email, passphrase):
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            return False

        user = users.get(email)
        if not user:
            return False
        
        salt = user["salt"]
        passphrase_salted = passphrase + salt
        passphrase_hash = hashlib.sha256(passphrase_salted.encode()).hexdigest()

        return passphrase_hash == user["pass_hash"]