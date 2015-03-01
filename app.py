from libbiopacndt_py import Client, ConnectionFailure

try:
    with Client(["A1", "A15"]) as client:
        data = client.poll("A15").next()
except ConnectionFailure as error:
    print "Failed to connect to {0} on port {1}.".format(error.args[0], error.args[1])
