class InvalidPortError(Exception):
    def __init__(self, node, port):
        self.node = node
        self.port = port

    def __str__(self):
        return f'Node "{self.node}" has no port "{self.port}"'
