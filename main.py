import tkinter as tk

# Tạo cửa sổ
root = tk.Tk()
root.title("Ứng dụng đầu tiên của tôi")
root.geometry("400x200")  # width x height

# Tạo tiêu đề
label = tk.Label(root, text="Xin chào!", font=("Segoe UI", 16))
label.pack(pady=20)

# Nút nhấn
def say_hello():
    label.config(text="Chào bạn nha!")

button = tk.Button(root, text="Nhấn để chào", command=say_hello)
button.pack()

# Vòng lặp hiển thị
root.mainloop()