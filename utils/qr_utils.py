import qrcode # Thư viện tạo mã QR
import base64 # Thư viện mã hóa base64
import json 
from datetime import datetime
import cv2 # Thư viện OpenCV để đọc mã QR
from config import KEY_FOLDER, PUBLIC_KEY_BOOK # Thư viện cấu hình chứa đường dẫn thư mục khóa và sổ public key

def generate_qr_for_public_key(email):
    path = f"{KEY_FOLDER}/{email}_info.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            info = json.load(f)
        with open(info["public_key_file"], "rb") as f:
            pub_key_raw = f.read()
    except FileNotFoundError:
        return False, "Không tìm thấy khóa công khai."

    # Tạo payload QR: email + created + public_key (base64)
    payload = {
        "email": info["email"],
        "created": info["created"],
        "public_key": base64.b64encode(pub_key_raw).decode()
    }

    data_str = json.dumps(payload) # Chuyển đổi payload thành chuỗi JSON
    img = qrcode.make(data_str)

    img_path = f"{KEY_FOLDER}/{email}_qrcode.png"
    img.save(img_path)

    return True, img_path

def read_qr_from_image(file_path):
    try:
        detector = cv2.QRCodeDetector() # Tạo đối tượng QRCodeDetector từ OpenCV
        img = cv2.imread(file_path) # imread để đọc ảnh từ file
        if img is None:
            return False, "Không đọc được ảnh."

        data, bbox, _ = detector.detectAndDecode(img)
        if not data:
            return False, "Không tìm thấy mã QR trong ảnh."

        json_data = json.loads(data)
        return True, json_data
    except Exception as e:
        return False, str(e)

def save_public_key_entry(data):
    # Lưu public key đã nhận được từ QR vào sổ
    try:
        with open(PUBLIC_KEY_BOOK, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if content:
                db = json.loads(content)
            else:
                db = {}
    except FileNotFoundError:
        db = {}

    email = data["email"]
    db[email] = {
        "public_key": data["public_key"],
        "created": data["created"],
        "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    with open(PUBLIC_KEY_BOOK, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2) # indent=2 để dễ đọc (2 space indent)