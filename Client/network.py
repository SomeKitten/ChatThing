import os
import socket
import time

import crypto


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.server = "74.102.2.15"
        # self.port = 63617
        with open("settings.txt", "rt") as f:
            contents = f.read()
            print(contents)
            contents = contents.split("\n")
            for content in contents:
                if content.split(":")[0] == "server":
                    self.server = content.split(":")[1]
                if content.split(":")[0] == "port":
                    self.port = int(content.split(":")[1])
        self.addr = (self.server, self.port)
        self.connect()

    def connect(self):
        print("Connecting to server...")
        try:
            self.client.connect(self.addr)
        except socket.error as e:
            print(str(e))

    def send(self, data):
        try:
            print("Sending: {}".format(data))
            self.client.send(str.encode(data))
        except socket.error as e:
            print(str(e))

    def get_data(self):
        while True:
            data = self.client.recv(2048).decode()
            print("Data Received: {}".format(data))

            if not data:
                print("Disconnected")
                break
            else:
                return data
        print("Lost connection...")
        self.client.close()
