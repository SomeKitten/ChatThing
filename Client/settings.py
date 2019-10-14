import _tkinter
import tkinter as tk


class Settings(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.username = ""
        self.rename = None
        self.master.geometry('200x50')
        self.create_widgets()

    def create_widgets(self):
        self.name = tk.Text(self)
        self.name['height'] = 1
        self.name.pack()

        self.save = tk.Button(self, text="SAVE", fg="green",
                              command=self.change_username)
        self.save.pack(side="bottom", fill='x')

    def change_username(self):
        self.username = self.name.get(1.0, "end")
        self.rename(self.username)


def run_settings(root, rename, username):
    app = Settings(master=root)

    app.username = username
    app.rename = rename

    app.name.insert("end", app.username)

    while tk.Toplevel.winfo_exists(root):
        app.update_idletasks()
        app.update()
