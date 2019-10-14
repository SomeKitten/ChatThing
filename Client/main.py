import os
import time
import tkinter as tk
from _thread import *

import crypto
import login
import network
import settings
import strconvert

fontsize = 12


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        self.master.geometry('500x500')
        self.username = ""
        self.version = "0.0.6"
        self.create_widgets()

    def _msg_return(self, event):
        self.send_msg()
        return "break"

    def _on_mousewheel(self, event):
        self.chat_container.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def create_widgets(self):
        # create the menu where all the buttons are at the bottom
        self.create_widgets_menu()
        # create the chatbox where the user types their messages
        self.create_widgets_chatbox()

        self.chat_text = tk.StringVar()

        # create the chat where all the messages are displayed
        self.create_widgets_chat()

        # display version
        self.chat_text.set("--- BruhChat v{} ---".format(self.version))

    def create_widgets_chat(self):
        self.chat_container = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self.chat_container, orient='vertical')
        self.chat_container.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar.config(command=self.chat_container.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.chat_frame = tk.Frame(self.chat_container)
        self.chat_container.pack(side="bottom", fill='both', expand=True)

        self.chat_container.create_window(0, 0, window=self.chat_frame, anchor="nw")
        self.chatmessages = tk.Label(self.chat_frame, font=("Helvetica", fontsize), textvariable=self.chat_text,
                                     justify="left", anchor='sw')
        self.chatmessages.pack(side="bottom", fill='both')

        self.chat_container.bind_all("<MouseWheel>", self._on_mousewheel)

    def create_widgets_chatbox(self):
        self.chatbox = tk.Text(self, font=("Helvetica", fontsize))
        self.chatbox.pack(side="bottom", fill='x')
        self.chatbox["height"] = 4
        self.chatbox.bind("<Return>", self._msg_return)

    def create_widgets_menu(self):
        self.menu = tk.Frame(self)  # container for buttons at bottom of window
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

    def get_cache(self, data):
        print("Updating cache...")
        crypto.write_b64("cache/login", data.encode())

    def get_data(self):
        while True:
            data = n.get_data()

            if data.startswith("0"):
                data = data[1:]
                self.get_messages(data)
            elif data.startswith("1"):
                data = data[1:]
                self.get_cache(data)
            elif data.startswith("2"):
                data = data[1:]
                self.get_username(data)
            elif data.startswith("3"):
                self.send_cache()
            n.client.send(str.encode("X"))

    def get_messages(self, data):
        datatime = data.split("|")[0]
        datatime = time.strftime('%H:%M:%S', time.localtime(float(datatime)))
        data = "0{}{}".format("[{}]".format(datatime).ljust(12), data.split("|")[1])[1:].strip()
        global new_messages
        new_messages = "{}\n{}".format(new_messages, data)

    def get_username(self, data):
        app.username = data

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

    def send_cache(self):
        try:
            login_cache = crypto.read_b64("cache/login")
            n.send("3{}".format(login_cache))
        except FileNotFoundError:
            pass

    def send_login(self, username, password):
        n.send("2{}\n{}".format(username, password))

    def send_msg(self):
        msg = self.chatbox.get(1.0, "end")
        msg = strconvert.add_emotes(msg).encode('utf-16', 'surrogatepass').decode('utf-16')
        if msg.strip() != "":
            n.send("1{}".format(msg))
            self.chatbox.delete(1.0, "end")

    def settings_event(self):
        global options
        if options is None or not tk.Toplevel.winfo_exists(options):
            options = tk.Toplevel()
            settings.run_settings(options, self.rename, self.username)
        else:
            options.destroy()
            options = None

    def update_chat(self):
        global new_messages
        print("Updating chat with: '{}'".format(new_messages))
        new_messages = strconvert.with_surrogates(new_messages)
        self.chat_text.set("{}\n{}".format(self.chat_text.get(), new_messages).strip())
        new_messages = ""
        self.update()
        self.chat_container.config(scrollregion=self.chat_container.bbox('all'))
        self.chat_container.yview_moveto(1)


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

start_new_thread(app.get_data, ())
while True:
    new_messages = new_messages.strip()
    if new_messages != "":
        app.update_chat()
    app.update_idletasks()
    app.update()
