# Based on http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python

import socket
import errno
from struct import unpack_from
import threading


class SockThread(threading.Thread):
    def __init__(self, channel, connection_info):
        super(SockThread, self).__init__()
        self.buffer = []

        self.alive = threading.Event()
        self.alive.set()
        self.quit = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(connection_info)
        except socket.error as error:
            if error.errno != errno.ECONNREFUSED:
                raise error
            else:
                print("Error connecting to {0} on port {1}.".format(server, port))
        self.sock.send(str(channel) + "\n")

    def run(self):
        while self.alive.isSet():
            if not self.quit:
                data = unpack_from("!d", self.sock.recv(1024))
                self.buffer.append(data[0])
            else:
                self.sock.close()
                break

    def poll(self):
        data = self.buffer
        self.buffer = []
        return data
