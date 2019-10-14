import os
import socket
import time
from _thread import *
import sys
import crypto

try:
    if not os.path.exists("settings.txt"):
        print("Creating new settings.txt...")
        f = open("settings.txt", "w+")
        local_ip = socket.gethostbyname(socket.gethostname())
        f.write("local_ip:{}\nport:{}".format(local_ip, 61797))
        f.close()
except FileExistsError:
    pass

# local_ip = "192.168.1.9"
# port = 63617

with open("settings.txt", "rt") as f:
    contents = f.read().split("\n")
    for content in contents:
        if content.split(":")[0] == "local_ip":
            local_ip = content.split(":")[1]
        if content.split(":")[0] == "port":
            port = int(content.split(":")[1])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((local_ip, port))
except socket.error as e:
    print(str(e))

s.listen(4)
print("Server started on port {}...".format(port))

log = ""

try:
    os.mkdir("logs")
except FileExistsError:
    pass

try:
    os.mkdir("cache")
except FileExistsError:
    pass

try:
    os.mkdir("local_cache")
except FileExistsError:
    pass

try:
    with open("logs/server.log", "rt+", encoding='utf-8') as f:
        log = f.read()
        print(log)
except FileNotFoundError:
    pass


def send_log(conn):
    global log
    print("Sending chat log...")
    for line in log.split("\n"):
        if line.strip() != "":
            conn.send(str.encode("0{}\n".format(line)))
            conn.recv(2048)
    print("Chat log sent!")


def change_name(number, name):
    if not os.path.exists("cache/{}".format(name)):
        names[number] = name
        print("Changing name")


def send_msg(name, msg):
    global log
    msg = "{}|{}: {}".format(time.time(), name, msg)
    send_text(msg)


def send_text(msg):
    global log
    log = "{}\n{}".format(log, msg)
    with open("logs/server.log", "wb+") as f:
        f.write(str.encode(log))
    msg = "0{}".format(msg)
    print("Sending: '{}'".format(msg))
    for c in conns:
        c.sendall(str.encode(msg))


def login_register(password, username, number):
    try:
        if os.path.exists("cache/{}".format(username)):
            reply = crypto.try_login(password, username, ips[number])
            if reply is None:
                return
        else:
            crypto.register(password, username)
            reply = crypto.try_login(password, username, ips[number])
        names[number] = username
        conn = conns[number]

        reply = "1{}".format(reply)
        print("Sending: '{}'".format(reply))
        conn.sendall(str.encode(reply))

        conn.recv(2048)

        reply = "2{}".format(username)
        print("Sending: '{}'".format(reply))
        conn.sendall(str.encode(reply))
    except AttributeError:
        pass


def token_login(token, number):
    try:
        if os.path.exists("local_cache/{}".format(ips[number])):
            try:
                credentials = crypto.token_login(ips[number], token).decode()
            except ValueError:
                os.remove("local_cache/{}".format(ips[number]))
                return
            credentials = credentials.split("\n")

            cache = crypto.try_login(credentials[0], credentials[1], ips[number])
            if cache:
                names[number] = credentials[1]
                conn = conns[number]

                reply = "1{}".format(cache)
                print("Sending: '{}'".format(reply))
                conn.sendall(str.encode(reply))

                conn.recv(2048)

                reply = "2{}".format(names[number])
                print("Sending: '{}'".format(reply))
                conn.sendall(str.encode(reply))
    except AttributeError:
        pass


def threaded_client(conn, number):
    global log
    names.append("Anonymous{}".format(number))
    print("Sending default name...")
    conn.send(str.encode("2{}".format(names[number])))  # change local username
    conn.recv(2048)

    send_log(conn)

    conn.send(str.encode("3"))  # prompt cache send

    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")

            if reply == "X":
                continue

            if not reply.startswith("2"):
                print("Unfiltered reply: '{}'".format(reply))

            if reply.startswith("0"):
                # name change
                name = reply[1:].strip()
                change_name(number, name)
            elif reply.startswith("1"):
                # generic text
                msg = reply[1:].strip()
                send_msg(names[number], msg)
            elif reply.startswith("2"):
                # log in
                tokens = reply[1:].split("\n")
                login_register(tokens[0], tokens[1], number)
            elif reply.startswith("3"):
                print("Token login!")
                token_login(reply[1:], number)
            if not data:
                print("Disconnected")
                break
            else:
                print("Sending: X")
                conn.sendall(str.encode("X"))
        except ConnectionResetError:
            break
    print("{} has left the chat...".format(names[number]))
    conns.remove(conn)
    conn.close()
    for c in conns:
        try:
            c.sendall(str.encode("{} has left the chat...".format(names[number])))
        except WindowsError:
            pass


connections = 0
conns = []
names = []
ips = []

while True:
    connection, addr = s.accept()
    print("Connected to:{}".format(addr))
    conns.append(connection)
    ips.append(addr[0])
    start_new_thread(threaded_client, (connection, connections, ))
    connections = connections + 1
