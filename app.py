import tkinter as tk
from panels.login_panel import LoginFrame
from panels.register_panel import RegisterFrame
from panels.dashboard_panel import DashboardFrame

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("An ninh máy tính - Demo")
        self.geometry("500x500")
        self.current_user = None
        self.frames = {}

        for F in (LoginFrame, RegisterFrame, DashboardFrame):
            frame = F(self)
            self.frames[F.__name__] = frame # __name__ hiển thị tên class hiện tại, thuộc tính có sẵn trong class
            frame.place(relwidth=1, relheight=1) # đặt frame chiếm toàn bộ chiều rộng và chiều cao của cửa sổ

        self.show_frame("LoginFrame")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise() # đặt frame lên trên cùng của app        

if __name__ == "__main__":
    app = App()
    app.mainloop()
