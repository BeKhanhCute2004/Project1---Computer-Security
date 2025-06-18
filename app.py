import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("An ninh máy tính - Demo")
        self.geometry("500x300")
        self.frames = {}

        for F in (LoginFrame, RegisterFrame):
            frame = F(self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Đăng nhập", font=("Segoe UI", 14)).pack(pady=10)
        tk.Button(self, text="Đi tới Đăng ký", command=lambda: master.show_frame("RegisterFrame")).pack(pady=5)

class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Đăng ký", font=("Segoe UI", 14)).pack(pady=10)
        tk.Button(self, text="Quay lại Đăng nhập", command=lambda: master.show_frame("LoginFrame")).pack(pady=5)

if __name__ == "__main__":
    app = App()
    app.mainloop()
