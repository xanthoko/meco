class Broker:
    def __init__(self, name: str, transport_type: str):
        self.name = name
        self.transport_type = transport_type
        self.nodes = []

    def __repr__(self):
        return f'Broker: {self.name}'

    def __str__(self):
        return self.name


class Node:
    def __init__(self, name: str, broker: Broker):
        self.name = name
        self.broker = broker

        self.subscribers = []
        self.publishers = []
        self.rpc_services = []
        self.rpc_clients = []

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node, topic: str, message_schema: dict):
        self.parent = node
        self.topic = topic
        self.message_schema = message_schema

    def __repr__(self):
        return f'Publisher: "{self.parent}" at "{self.topic}"'


class Subscriber:
    def __init__(self, node, topic: str):
        self.parent = node
        self.topic = topic

    def __repr__(self):
        return f'Subscriber: "{self.parent}" at "{self.topic}"'


class RPC_Service:
    def __init__(self, node, name: str, message_schema: dict):
        self.parent = node
        self.name = name
        self.message_schema = message_schema

    def __repr__(self):
        return f'RPC Service: "{self.name}" of "{self.parent}"'


class RPC_Client:
    def __init__(self, node, name: str, message_schema: dict):
        self.parent = node
        self.name = name
        self.message_schema = message_schema

    def __repr__(self):
        return f'RPC Client: "{self.name}" of "{self.parent}"'


class BaseBridge:
    def __init__(self, name: str, brokerA: Broker, brokerB: Broker):
        self.name = name
        self.brokerA = brokerA
        self.brokerB = brokerB


class TopicBridge(BaseBridge):
    def __init__(self, from_topic: str, to_topic: str, *args, **kwargs):
        self.from_topic = from_topic
        self.to_topic = to_topic
        super(TopicBridge, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'Topic bridge: "{self.brokerA}"-"{self.brokerB}"'


class RPCBridge(BaseBridge):
    def __init__(self, nameA: str, nameB: str, *args, **kwargs):
        self.nameA = nameA
        self.nameB = nameB
        super(RPCBridge, self).__init__(*args, **kwargs)

    def __repr__(self):
        return f'RPC bridge: "{self.brokerA}"-"{self.brokerB}"'


class Proxy:
    def __init__(self, name: str, url: str, method: str, broker: Broker):
        self.name = name
        self.url = url
        self.method = method
        self.broker = broker

        self.rpc_service = None

    def as_dict(self):
        return {'name': self.name, 'method': self.method, 'url': self.url}

    def __repr__(self):
        return f'Proxy: "{self.name} at "{self.url}"'
