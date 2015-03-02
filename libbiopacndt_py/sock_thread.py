# Based on http://eli.thegreenplace.net/2011/05/18/code-sample-socket-client-thread-in-python

import socket
import errno
from struct import unpack_from
import threading

from libbiopacndt_py.client_exceptions import ConnectionFailure


class SockThread(threading.Thread):
    """Subclass of the thread class, specifically designed to fetch information from
    the biopac daemon. Stores information sock_thread.buffer, which is emptied
    every time sock_thread.poll() is called.

    Args:
        channel: the channel to connect to, as it appears in the manifest.
        connection_info: a tuple containing the server and port to connect on."""
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
        # ignore manifest
        while True:
            data = self.sock.recv(1024)
            if "\n" in data:
                break

    def run(self):
        """Fetch data from the server and store in the buffer."""
        while self.alive.isSet():
            packet = self.sock.recv(32)
            if len(packet) < 8:
                continue
            data = unpack_from("!d", packet)
            self.buffer.append(data[0])

    def join(self, timeout=None):
        """Shut down the thread. Close sockets and clear alive status. Not calling this
        will result in an app that doesn't shut down."""
        self.sock.close()
        self.alive.clear()
        threading.Thread.join(self, timeout)

    def poll(self):
        """Grab all the data in the buffer. Clears the buffer when called."""
        data = self.buffer
        self.buffer = []
        return data
