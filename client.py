import logging
import socket
from json import loads

from sock_threads.sock_threads import SockThread

channels = [("A1", 2000), ("A3", 2000)]


class Channel(object):
    def __init__(self, channel_name, sample_rate=20.0):
        self.channel_name = channel_name
        self.sample_rate = sample_rate

    def __str__(self):
        return "{" + '"index": "{0}", "sample_rate": {1}'.format(self.channel_name, self.sample_rate) + "}\n"


class Client(object):
    def __init__(self, channel_names, server='localhost', port=9999):
        logging.basicConfig(file="biopacndt_py.log", level=logging.INFO)

        self.server = server
        self.port = port
        self.channels = []
        self.sockets = {}
        self.channel_names = channel_names

        # get a list of the available channels
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.connect((server, port))
        except socket.error as error:
            if error.errno != errno.ECONNREFUSED:
                raise error
            else:
                print("Error connecting to {0} on port {1}.".format(server, port))
        data = ""
        while True:
            data += probe.recv(1024)
            if "\n" in data:
                break
        probe.close()

        # make a friendlier dict
        available_channels = loads(data)
        self.available_names = {}
        for channel in available_channels['channels']:
            self.available_names[channel['index']] = channel['sample_rate']

    def connect(self):
        # create sockets
        for name in self.channel_names:
            if name in self.available_names.keys():
                channel = Channel(name, self.available_names[name])
                self.channels.append(channel)

                sock_thread = SockThread(channel, (self.server, self.port))
                sock_thread.setDaemon(True)
                sock_thread.start()
                self.sockets[name] = sock_thread

                logging.info("Created channel {0}.".format(channel))
            else:
                logging.warning("Could not find channel \"{0}\" in manifest.".format(name))

    def poll(self, channel, num=None):
        data = self.sockets[channel].poll()
        i = 0
        if num is None:
            while data:
                yield data.pop()
        else:
            while i < num:
                if not data:
                    raise StopIteration()
                yield data.pop()
                i += 1


client = Client(["A1", "A15"])
client.connect()
import time
time.sleep(1)
for data in client.poll("A1",10):
    print data

"""
sockets = []
for channel in channels:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 9999))
    sockets.append(sock)
    sock.send(channel + "\n")

while True:
    for sock in sockets:
        buffer = sock.recv(1024)
        data = unpack_from("!d", buffer)
        print data[0]
"""