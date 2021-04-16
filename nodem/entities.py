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

    def __str__(self):
        return self.name


class InNode:
    def __init__(self, name: str, broker: Broker, commlib_node=None):
        self.name = name
        self.broker = broker
        self.commlib_node = commlib_node

        self.subscribers = []
        self.rpc_services = []

    def __repr__(self):
        return f'InNode: {self.name}'


class OutNode:
    def __init__(self, name: str, broker: Broker, commlib_node=None):
        self.name = name
        self.broker = broker
        self.commlib_node = commlib_node

        self.publishers = []
        self.rpc_clients = []

    def __repr__(self):
        return f'OutNode: {self.name}'


class Publisher:
    def __init__(self,
                 node: OutNode,
                 topic: str,
                 message_class: PubSubMessage,
                 commlib_publisher=None):
        self.node = node
        self.topic = topic
        self.message_class = message_class
        self.commlib_publisher = commlib_publisher

    def publish(self):
        if self.commlib_publisher:
            msg = self.message_class()
            self.commlib_publisher.publish(msg)
        else:
            print('[ERROR] Commlib publisher not set.')

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node: InNode, topic: str, commlib_subscriber=None):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = commlib_subscriber

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self,
                 node: InNode,
                 name: str,
                 message_class: RPCMessage,
                 on_request,
                 commlib_rpc_service=None):
        self.node = node
        self.name = name
        self.on_request = on_request
        self.message_class = message_class
        self.commlib_rpc_service = commlib_rpc_service

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.node}'


class RPC_Client:
    def __init__(self,
                 node: OutNode,
                 name: str,
                 message_module: RPCMessage,
                 commlib_rpc_client=None):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = commlib_rpc_client

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.node}'


class Bridge:
    def __init__(self, brokerA: Broker, brokerB: Broker, from_topic: str,
                 to_topic: str, commlib_bridge):
        self.brokerA = brokerA
        self.brokerB = brokerB
        self.from_topic = from_topic
        self.to_topic = to_topic

        self.commlib_bridge = commlib_bridge

    def __repr__(self):
        return f'Bridge {self.brokerA}-{self.brokerB}'
