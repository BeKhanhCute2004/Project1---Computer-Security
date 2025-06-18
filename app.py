import tkinter as tk
import json
import tkinter as tk
from tkinter import messagebox

USER_DB = "users.json"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("An ninh máy tính - Demo")
        self.geometry("500x300")
        self.frames = {}

        for F in (LoginFrame, RegisterFrame):
            frame = F(self)
            self.frames[F.__name__] = frame # __name__ hiển thị tên class hiện tại, thuộc tính có sẵn trong class
            frame.grid(row=0, column=0, sticky="nsew") # kéo frame full khung hình bắt đầu từ dòng 0 cột 0

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise() # đặt frame lên trên cùng của app

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Đăng nhập", font=("Segoe UI", 14)).pack(pady=10)

        self.email_entry = tk.Entry(self, width=30)
        self.email_entry.pack(pady=5)
        self.pw_entry = tk.Entry(self, width=30, show="*")
        self.pw_entry.pack(pady=5)

        tk.Button(self, text="Đăng nhập", command=self.login).pack(pady=8) # không cần lambda vì không có đối số
        tk.Button(self, text="Chưa có tài khoản?", command=lambda: master.show_frame("RegisterFrame")).pack() # dùng lambda vì phải nhận đối số. Nếu nhập command=master.show_frame("RegisterFrame") python sẽ hiểu thực thi lệnh ngay và trả về giá trị ở phần return của hàm gây lỗi.

    def login(self):
        email = self.email_entry.get().strip() #strip() để loại bỏ các ký tự khoảng trắng
        pw = self.pw_entry.get().strip()

        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        user = users.get(email)
        if not user or user["passphrase"] != pw:
            messagebox.showerror("Lỗi", "Sai email hoặc passphrase!")
        else:
            messagebox.showinfo("Chào", f"Xin chào {user['name']}!")
            # Chuyển sang dashboard nếu có sau này

class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Đăng ký tài khoản", font=("Segoe UI", 14)).pack(pady=10)

        # Khung nhập liệu
        form = tk.Frame(self)
        form.pack()

        self.inputs = {}
        labels = ["Email", "Họ tên", "Passphrase"]

        for i, label in enumerate(labels):
            tk.Label(form, text=label + ":").grid(row=i, column=0, sticky="e", padx=5, pady=4) # đặt các nhãn vào lưới, sticky east kéo nhãn đến hết bên phải
            entry = tk.Entry(form, width=30, show="*" if label == "Passphrase" else "") # tạo ô nhập liệu
            entry.grid(row=i, column=1, pady=4) # gán vào cột 2 cùng dòng với các nhãn
            self.inputs[label] = entry

        tk.Button(self, text="Đăng ký", command=self.register).pack(pady=10)
        tk.Button(self, text="← Quay lại đăng nhập", command=lambda: master.show_frame("LoginFrame")).pack()

    def register(self):
        email = self.inputs["Email"].get().strip()
        name = self.inputs["Họ tên"].get().strip()
        pw = self.inputs["Passphrase"].get().strip()

        if not email or not name or not pw:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ thông tin.")
            return

        # Lưu vào file JSON
        try:
            with open(USER_DB, "r", encoding="utf-8") as f:
                users = json.load(f)
        except FileNotFoundError:
            users = {}

        if email in users:
            messagebox.showerror("Trùng email", "Email này đã được đăng ký.")
            return

        users[email] = {
            "name": name,
            "passphrase": pw
        }

        with open(USER_DB, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False) # ghi users vào f dưới dạng json. indent: thụt 2 space, ensure_ascii: Đảm bảo các ký tự tiếng Việt không bị chuyển thành mã ASCII.

        messagebox.showinfo("Thành công", "Đăng ký thành công!")
        self.master.show_frame("LoginFrame")

if __name__ == "__main__":
    app = App()
    app.mainloop()
