import logging
import socket
import errno
from json import loads

from sock_thread import SockThread
from client_exceptions import ConnectionFailure, ChannelNotFound


class Channel(object):
    """ Just a simple datatype that holds channel information and prints it out
    in a friendly format.

    Args:
        channel_name: the name on the manifest. Usually known beforehand.
        sample_rate: if you want to specify a sample rate, do it here, otherwise
            just let the manifest tell you what it is."""
    def __init__(self, channel_name, sample_rate=20.0):
        self.channel_name = channel_name
        self.sample_rate = sample_rate

    def __str__(self):
        return "{" + '"index": "{0}", "sample_rate": {1}'.format(self.channel_name, self.sample_rate) + "}"


class Client(object):
    """ The actual client for talking to the biopac daemon. Creates a threaded socket
    for each channel you connect to and stores that information in a per-channel buffer.

    Args:
        channel_names: a list of names of channels that you want to connect to,
            as they appear in the manifest.
        server: address of the server you're connecting to.
        port: port number."""
    def __init__(self, channel_names, server='localhost', port=9999):
        logging.basicConfig(file="biopacndt_py.log", level=logging.INFO)

        self.server = server
        self.port = port
        self.channels = []
        self.sockets = {}
        self.buffer = {}
        self.channel_names = channel_names

        # get a list of the available channels
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.connect((server, port))
        except socket.error as error:
            if error.errno != errno.ECONNREFUSED:
                raise error
            else:
                raise ConnectionFailure(server, port)
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

    def connect(self, ignore_missing_channels=True):
        """Create the sockets and connect to the server.

        Args:
            ignore_missing_channels (optional): if True, channels not found in
                the manifest will be noted in the log. If False, missing channels will
                raise a ChannelNotFound exception."""
        for name in self.channel_names:
            if name in self.available_names.keys():
                channel = Channel(name, self.available_names[name])
                self.channels.append(channel)

                sock_thread = SockThread(channel, (self.server, self.port))
                sock_thread.setDaemon(True)
                sock_thread.start()
                self.sockets[name] = sock_thread
                self.buffer[name] = []

                logging.info("Created channel {0}".format(channel))
            else:
                if not ignore_missing_channels:
                    raise ChannelNotFound(name)
                else:
                    logging.warning("Could not find channel \"{0}\" in manifest.".format(name))

    def disconnect(self):
        """Disconnect by closing the sockets and merging threads."""
        for sock_name, sock_thread in self.sockets.items():
            sock_thread.join()

    def poll(self, channel):
        """A generator that returns the data out of the buffer, per channel.

        If you want a certain number of items, use:

        for i in range(10):
            data = client.poll("A1").next()

        Args:
            channel: the name of the channel as it appears in the manifest."""
        # extend our buffer because polling the sock_thread clears
        # its own buffer
        self.buffer[channel].extend(self.sockets[channel].poll())
        while self.buffer[channel]:
            yield self.buffer[channel].pop(0)
