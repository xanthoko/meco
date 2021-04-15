from commlib.endpoints import TransportType
from commlib.msg import PubSubMessage, RPCMessage


class Broker:
    def __init__(self, name: str, connection_params: dict,
                 transport_type: TransportType):
        self.name = name
        self.connection_params = connection_params
        self.transport_type = transport_type
        self.commlib_broker = None

    def __repr__(self):
        return self.name


class InNode:
    def __init__(self, name: str, broker: Broker):
        self.name = name
        self.broker = broker

        self.subscribers = []
        self.rpc_services = []

    def __repr__(self):
        return f'InNode: {self.name}'


class OutNode:
    def __init__(self, name: str, broker: Broker):
        self.name = name
        self.broker = broker

        self.publishers = []
        self.rpc_clients = []

    def __repr__(self):
        return f'OutNode: {self.name}'


class Publisher:
    def __init__(self, node: OutNode, topic: str, message_module: PubSubMessage):
        self.node = node
        self.topic = topic
        self.commlib_publisher = None
        self.message_module = message_module

    def publish(self):
        if self.commlib_publisher:
            msg = self.message_module()
            self.commlib_publisher.publish(msg)
        else:
            print('[ERROR] Commlib publisher not set.')

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node: InNode, topic: str):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self, node: InNode, name: str, message_module: RPCMessage):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.on_request = None
        self.commlib_rpc_service = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.node}'


class RPC_Client:
    def __init__(self, node: OutNode, name: str, message_module: RPCMessage):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.node}'
