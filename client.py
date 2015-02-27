import socket
import errno
from struct import unpack_from
import logging
from json import loads

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
        self.sockets = []

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
        available_names = {}
        for channel in available_channels['channels']:
            available_names[channel['index']] = channel['sample_rate']

        # create sockets
        for name in channel_names:
            if name in available_names.keys():
                channel = Channel(name, available_names[name])
                self.channels.append(channel)

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((server, port))
                sock.send(str(channel) + "\n")
                self.sockets.append(sock)

                logging.info("Created channel {0}.".format(channel))
            else:
                logging.warning("Could not find channel \"{0}\" in manifest.".format(name))


client = Client(["A3"])

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