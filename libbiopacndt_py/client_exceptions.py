import exceptions


class ConnectionFailure(exceptions.Exception):
    pass


class ChannelNotFound(exceptions.Exception):
    pass