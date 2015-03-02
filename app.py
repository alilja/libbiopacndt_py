import time
import sys

from libbiopacndt_py import Client, ConnectionFailure

try:
    client = Client(["A1"])
except ConnectionFailure as error:
    print "Failed to connect to {0} on port {1}.".format(error.args[0], error.args[1])

client.connect()
while True:
    try:
        try:
            print client.poll("A1").next()
        except StopIteration:
            continue
    except KeyboardInterrupt:
        client.disconnect()
        sys.exit()
client.disconnect()
