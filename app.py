import time

from libbiopacndt_py import Client, ConnectionFailure

try:
    client = Client(["A1"])
except ConnectionFailure as error:
    print "Failed to connect to {0} on port {1}.".format(error.args[0], error.args[1])

client.connect()
time.sleep(3)
for i in range(50):
    data = client.poll("A1").next()
    print data
client.disconnect()
