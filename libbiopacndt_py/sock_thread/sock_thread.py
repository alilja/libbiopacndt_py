# Based on http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python

import socket
import errno
from struct import unpack_from
import threading

from libbiopacndt_py.client_exceptions import ConnectionFailure


class SockThread(threading.Thread):
    def __init__(self, channel, connection_info):
        super(SockThread, self).__init__()
        self.buffer = []

        self.alive = threading.Event()
        self.alive.set()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(connection_info)
        except socket.error as error:
            if error.errno != errno.ECONNREFUSED:
                raise error
            else:
                raise ConnectionFailure(connection_info[0], connection_info[1])
        self.sock.send(str(channel) + "\n")

    def run(self):
        while self.alive.isSet():
            data = unpack_from("!d", self.sock.recv(32))
            self.buffer.append(data[0])

    def join(self, timeout=None):
        self.sock.close()
        self.alive.clear()
        threading.Thread.join(self, timeout)

    def poll(self):
        data = self.buffer
        self.buffer = []
        return data
