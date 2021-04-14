from importlib import import_module

from commlib.endpoints import TransportType
from commlib.msg import PubSubMessage, RPCMessage

from nodem.utils import typecasted_value


class Broker:
    def __init__(self, name: str, connection_params: dict,
                 transport_type: TransportType):
        self.name = name
        self.connection_params = connection_params
        self.transport_type = transport_type
        self.commlib_broker = None

    def __repr__(self):
        return self.name


class Node:
    """The parent class that contains the service entities i.e. publishers, subscribers
    rpc_services and rpc_clients along with the given properties for the node."""
    def __init__(self, name, properties, broker: Broker):
        self.name = name
        self.broker = broker

        self._properties = []
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.set_properties(properties)

        self.commlib_node = None

    def set_properties(self, object_model):
        """
        Args:
            object_model (textx Object model): Object model that has the properties
                field.
        """
        if not object_model:
            return
        node_properties = object_model.properties
        for node_property in node_properties:
            # node property has 'type', 'default' and 'name' fields
            setattr(self, node_property.name, typecasted_value(node_property))
            self._properties.append(node_property.name)

    @property
    def properties(self):
        return {x: getattr(self, x) for x in self._properties}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node: Node, topic: str, message_module: PubSubMessage):
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
    def __init__(self, node: Node, topic: str):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self, node: Node, name: str, message_module: RPCMessage):
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
    def __init__(self, node: Node, name: str, message_module: RPCMessage):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.node}'
