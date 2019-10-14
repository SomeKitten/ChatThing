import _tkinter
import tkinter as tk


class Settings(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.login = None
        self.master.geometry('200x100')
        self.create_widgets()

    def create_widgets(self):
        self.name = tk.Text(self)
        self.name['height'] = 1
        self.name.pack()

        self.password = tk.Text(self)
        self.password['height'] = 1
        self.password.pack()

        self.login_button = tk.Button(self, text="LOGIN", fg="green",
                              command=self.send_login)
        self.login_button.pack(side="bottom", fill='x')

    def send_login(self):
        username = self.name.get(1.0, "end").strip().replace("\n", "")
        password = self.password.get(1.0, "end").strip().replace("\n", "")
        print("ITEMS\n{}\n{}".format(password, username))
        self.login(password, username)


def run_login(root, login):
    app = Settings(master=root)

    app.login = login

    while tk.Toplevel.winfo_exists(root):
        app.update_idletasks()
        app.update()
