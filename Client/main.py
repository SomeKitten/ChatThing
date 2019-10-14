import os
import tkinter as tk
import network
from _thread import *
import settings
import login
import crypto
import strconvert

fontsize = 12


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.master.geometry('500x500')
        self.username = ""
        self.create_widgets()

    def create_widgets(self):

        self.menu = tk.Frame(self)
        self.menu.pack(side="bottom")

        self.quit = tk.Button(self.menu, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="left")

        self.settings = tk.Button(self.menu, text="SETTINGS", fg="black",
                              command=self.settings_event)
        self.settings.pack(side="left")

        self.login = tk.Button(self.menu, text="LOGIN", fg="green",
                              command=self.login_event)
        self.login.pack(side="left")

        # divider
        # divider
        # divider
        # divider

        self.chatbox = tk.Text(self, font=("Helvetica", fontsize))
        self.chatbox.pack(side="bottom", fill='x')
        self.chatbox["height"] = 4
        self.chatbox.bind("<Return>", self.msg_return)

        # divider
        # divider
        # divider
        # divider

        self.chat_container = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self.chat_container, orient='vertical')
        self.chat_container.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.chat_container.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.chat_frame = tk.Frame(self.chat_container)
        self.chat_container.pack(side="bottom", fill='both', expand=True)

        self.chat_container.create_window(0, 0, window=self.chat_frame, anchor="nw")

        self.chat_text = tk.StringVar()
        self.chatmessages = tk.Label(self.chat_frame, font=("Helvetica", fontsize), textvariable=self.chat_text, justify="left", anchor='sw')
        self.chatmessages.pack(side="bottom", fill='both')

        self.chat_container.bind_all("<MouseWheel>", self._on_mousewheel)

        # divider
        # divider
        # divider
        # divider

        self.chat_text.set("--- BruhChat v0.0.5 ---")

    def _on_mousewheel(self, event):
        self.chat_container.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def send_msg(self):
        msg = self.chatbox.get(1.0, "end")
        msg = strconvert.add_emotes(msg).encode('utf-16', 'surrogatepass').decode('utf-16')
        if msg.strip() != "":
            n.send("1{}".format(msg))
            self.chatbox.delete(1.0, "end")

    def update_chat(self):
        while True:
            msg = n.update_chat()

            if msg.startswith("2"):
                app.username = msg[1:]
                continue
            if msg.startswith("3"):
                try:
                    login_cache = crypto.read_b64("cache/login")
                    n.send("3{}".format(login_cache))
                except FileNotFoundError:
                    pass

            if msg is not None and msg.startswith("0"):
                msg = msg[1:].strip()
                global new_messages
                new_messages = "{}\n{}".format(new_messages, msg)

    def msg_return(self, event):
        self.send_msg()
        return "break"

    def settings_event(self):
        global options
        if options is None or not tk.Toplevel.winfo_exists(options):
            options = tk.Toplevel()
            settings.run_settings(options, self.rename, self.username)
        else:
            options.destroy()
            options = None

    def login_event(self):
        global login_window
        if login_window is None or not tk.Toplevel.winfo_exists(login_window):
            login_window = tk.Toplevel()
            login.run_login(login_window, self.send_login)
        else:
            login_window.destroy()
            login_window = None

    def rename(self, new_name):
        self.username = new_name
        n.send("0{}".format(self.username))

    def send_login(self, username, password):
        n.send("2{}\n{}".format(username, password))


try:
    os.mkdir("cache")
except FileExistsError:
    pass

try:
    if not os.path.exists("settings.txt"):
        print("Creating new settings.txt...")
        f = open("settings.txt", "w+")
        f.write("server:74.102.2.15\nport:61797")
        f.close()
except FileExistsError:
    pass

options = None
login_window = None
new_messages = ""

n = network.Network()

root = tk.Tk()
app = Application(master=root)

app.username = ""

start_new_thread(app.update_chat, ())
while True:
    if new_messages.strip() != "":
        new_messages = new_messages.strip()
        print("Updating chat with: '{}'".format(new_messages))
        new_messages = strconvert.with_surrogates(new_messages)
        app.chat_text.set("{}\n{}".format(app.chat_text.get(), new_messages).strip())
        new_messages = ""
        app.update()
        app.chat_container.config(scrollregion=app.chat_container.bbox('all'))
        app.chat_container.yview_moveto(1)
    app.update_idletasks()
    app.update()
