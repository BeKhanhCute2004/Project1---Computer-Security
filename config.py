import datetime

USER_DB = "data/users.json"
KEY_FOLDER = "rsa_keys"
PUBLIC_KEY_BOOK = "data/public_keys.json"

def log_event(message):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {message}\n")