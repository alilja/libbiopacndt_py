#!/usr/bin/env python
from optparse import OptionParser
import sys

from client import Client, ConnectionFailure

parser = OptionParser(usage="usage: %prog [options] channel1 channel2 ... channeln")
parser.add_option("-v", "--verbose", action="store_true")
parser.add_option(
    "-i",
    "--ignore",
    help=(
        "Do not ignore missing channels. Otherwise, channels "
        "that are entered that do not appear in the manifest "
        "will not cause an exception."
    ),
    action="store_false"
)
parser.add_option(
    "-s",
    "--server",
    help="The server address of the Biopac daemon."
)
parser.add_option(
    "-p",
    "--port",
    type="int",
    help="The port number of the Biopac daemon."
)

if __name__ == "__main__":
    (options, args) = parser.parse_args()

    try:
        client = Client(
            args,
            server=options.server,
            port=options.port,
            verbose=options.verbose,
            ignore_missing_channels=options.ignore,
        )
    except ConnectionFailure as error:
        print "Failed to connect to {0} on port {1}.".format(error.args[0], error.args[1])
        sys.exit()

    client.connect()
    while True:
        try:
            try:
                output = []
                for channel in args:
                    output.append("{0}: {1}".format(channel, round(client.poll(channel).next(), 2)))
                print "    ".join(output)
            except StopIteration:
                continue
        except KeyboardInterrupt:
            sys.exit()
