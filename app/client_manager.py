

class ClientManager(object):

    # Connect client player to handler
    connections = dict()

    @classmethod
    def add(cls, connect_key, handler):
        cls.connections[connect_key] = handler

    @classmethod
    def remove(cls, connect_key):
        del cls.connections[connect_key]

    @classmethod
    def send_message(cls, connect_key, data):
        handler = cls.connections[connect_key]
        handler._send_message(**data)
