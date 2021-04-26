from commlib.node import Node as CommNode
from commlib.endpoints import TransportType
from commlib.msg import PubSubMessage, RPCMessage
from nodem.logic import default_on_message, default_on_request


class Broker:
    def __init__(self, name: str, connection_params: dict,
                 transport_type: TransportType):
        self.name = name
        self.connection_params = connection_params
        self.transport_type = transport_type
        self.type = self.transport_type.name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Publisher:
    def __init__(self, node, topic: str, message_class: PubSubMessage):
        self.parent = node
        self.topic = topic
        self.message_class = message_class
        self.commlib_publisher = self._create_commlib_publisher(
            topic, message_class, node.commlib_node)

    def publish(self, msg=None):
        msg = msg or self.message_class()
        self.commlib_publisher.publish(msg)

    def _create_commlib_publisher(self, topic: str, message_module,
                                  commlib_node: CommNode):
        return commlib_node.create_publisher(topic=topic, msg_type=message_module)

    def __repr__(self):
        return f'Publisher of: {self.parent}'


class Subscriber:
    def __init__(self, node, topic: str, on_message=None):
        self.parent = node
        self.topic = topic
        self.commlib_subscriber = self._create_commlib_subscriber(
            topic, node.commlib_node, on_message)

    def run(self):
        self.commlib_subscriber.run()

    def _create_commlib_subscriber(self, topic: str, commlib_node: CommNode,
                                   on_message):
        on_message = on_message or default_on_message
        return commlib_node.create_subscriber(topic=topic, on_message=on_message)

    def __repr__(self):
        return f'Subscriber of: {self.parent}'


class RPC_Service:
    def __init__(self, node, name: str, message_class: RPCMessage, on_request):
        self.parent = node
        self.name = name
        self.on_request = on_request
        self.message_class = message_class
        self.commlib_rpc_service = self._create_commlib_rpc_service(
            name, message_class, node.commlib_node, default_on_request)

    def _create_commlib_rpc_service(self, name: str, message_module, commlib_node,
                                    on_request):
        return commlib_node.create_rpc(rpc_name=name,
                                       msg_type=message_module,
                                       on_request=on_request)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.parent}'


class RPC_Client:
    def __init__(self, node, name: str, message_module: RPCMessage):
        self.parent = node
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = self._create_commlib_rpc_client(
            name, message_module, node.commlib_node)

    def _create_commlib_rpc_client(self, name: str, message_module, commlib_node):
        return commlib_node.create_rpc_client(rpc_name=name,
                                              msg_type=message_module)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.parent}'


class Proxy:
    def __init__(self, name: str, url: str, broker: Broker, node):
        self.name = name
        self.url = url
        self.broker = broker
        self.node = node

    def __repr__(self):
        return f'Proxy "{self.name} for "{self.url}"'
