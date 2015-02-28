from libbiopacndt_py import Client

if __name__ == "__main__":
    import time
    with Client(["A1", "A15"]) as client:
        for i in range(10):
            time.sleep(1)
            data = client.poll("A15").next()
            print data
