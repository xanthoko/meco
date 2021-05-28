from commlib.msg import PubSubMessage, RPCMessage
from commlib.node import Node as CommNode, TransportType
from commlib.bridges import (TopicBridge as CommTopBridge, TopicBridgeType,
                             RPCBridge as CommRPCBridge, RPCBridgeType)

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


class Node:
    def __init__(self, name: str, broker):
        self.name = name
        self.broker = broker
        self.commlib_node = self._create_commlib_node()

        self.subscribers = []
        self.rpc_services = []
        self.publishers = []
        self.rpc_clients = []

    def _create_commlib_node(self):
        return CommNode(node_name=self.name,
                        transport_type=self.broker.transport_type,
                        transport_connection_params=self.broker.connection_params,
                        debug=True)

    def __repr__(self):
        return f'Node {self.name}'


class Publisher:
    def __init__(self, parent, topic: str, message_class: PubSubMessage):
        self.parent = parent
        self.topic = topic
        self.message_class = message_class
        if isinstance(parent, Node):
            self.commlib_publisher = self._create_commlib_publisher(
                topic, message_class, parent.commlib_node)
        else:
            self.commlib_publisher = self._create_commlib_bare_publisher(
                topic, message_class, parent.broker)

    def publish(self, msg=None):
        msg = msg or self.message_class()
        self.commlib_publisher.publish(msg)

    def _create_commlib_publisher(self, topic: str, message_module,
                                  commlib_node: CommNode):
        return commlib_node.create_publisher(topic=topic, msg_type=message_module)

    def _create_commlib_bare_publisher(self, topic, message_module, broker):
        if broker.transport_type == TransportType.MQTT:
            from commlib.transports.mqtt import Publisher
        elif broker.transport_type == TransportType.AMQP:
            from commlib.transports.amqp import Publisher
        else:
            from commlib.transports.redis import Publisher
        return Publisher(topic=topic,
                         msg_type=message_module,
                         conn_params=broker.connection_params)

    def __repr__(self):
        return f'Publisher of: {self.parent}'


class Subscriber:
    def __init__(self, parent, topic: str, on_message=None):
        self.parent = parent
        self.topic = topic
        if isinstance(parent, Node):
            self.commlib_subscriber = self._create_commlib_subscriber(
                topic, parent.commlib_node, on_message)
        else:
            self.commlib_subscriber = self._create_commlib_bare_subscriber(
                topic, parent.broker, on_message)

    def run(self):
        self.commlib_subscriber.run()

    def _create_commlib_subscriber(self, topic: str, commlib_node: CommNode,
                                   on_message):
        on_message = on_message or default_on_message
        return commlib_node.create_subscriber(topic=topic, on_message=on_message)

    def _create_commlib_bare_subscriber(self, topic: str, broker: Broker,
                                        on_message):
        if broker.transport_type == TransportType.MQTT:
            from commlib.transports.mqtt import Subscriber
        elif broker.transport_type == TransportType.AMQP:
            from commlib.transports.amqp import Subscriber
        else:
            from commlib.transports.redis import Subscriber
        return Subscriber(topic=topic,
                          on_message=on_message,
                          conn_params=broker.connection_params)

    def __repr__(self):
        return f'Subscriber of: {self.parent}'


class RPC_Service:
    def __init__(self, parent, name: str, message_class: RPCMessage, on_request):
        self.parent = parent
        self.name = name
        self.on_request = on_request
        self.message_class = message_class
        self.commlib_rpc_service = self._create_commlib_rpc_service(
            name, message_class, parent.commlib_node, default_on_request)

    def run(self):
        self.commlib_rpc_service.run()

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
    def __init__(self, parent, name: str, message_module: RPCMessage):
        self.parent = parent
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = self._create_commlib_rpc_client(
            name, message_module, parent.commlib_node)

    def call(self, msg):
        return self.commlib_rpc_client.call(msg)

    def _create_commlib_rpc_client(self, name: str, message_module, commlib_node):
        return commlib_node.create_rpc_client(rpc_name=name,
                                              msg_type=message_module)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.parent}'


class BaseBridge:
    def __init__(self, name: str, brokerA: Broker, brokerB: Broker):
        self.name = name
        self.brokerA = brokerA
        self.brokerB = brokerB

    def run(self):
        self.commlib_bridge.run()

    def _create_commlib_bridge(self, commlib_bridge_class, bridge_type_class,
                               from_uri: str, to_uri: str):
        bridge_type = getattr(bridge_type_class,
                              f'{self.brokerA.type}_TO_{self.brokerB.type}')
        return commlib_bridge_class(
            bridge_type,
            from_uri=from_uri,
            to_uri=to_uri,
            from_broker_params=self.brokerA.connection_params,
            to_broker_params=self.brokerB.connection_params)


class TopicBridge(BaseBridge):
    def __init__(self, from_topic: str, to_topic: str, *args, **kwargs):
        self.from_topic = from_topic
        self.to_topic = to_topic
        super(TopicBridge, self).__init__(*args, **kwargs)

        self.commlib_bridge = self._create_commlib_bridge(CommTopBridge,
                                                          TopicBridgeType,
                                                          from_topic, to_topic)

    def __repr__(self):
        return f'Topic bridge {self.brokerA}-{self.brokerB}'


class RPCBridge(BaseBridge):
    def __init__(self, nameA: str, nameB: str, *args, **kwargs):
        self.nameA = nameA
        self.nameB = nameB
        super(RPCBridge, self).__init__(*args, **kwargs)

        self.commlib_bridge = self._create_commlib_bridge(CommRPCBridge,
                                                          RPCBridgeType, nameA,
                                                          nameB)

    def __repr__(self):
        return f'RPC bridge {self.brokerA}-{self.brokerB}'


class Proxy:
    def __init__(self, name: str, url: str, method: str, broker: Broker):
        self.name = name
        self.url = url
        self.method = method
        self.broker = broker

        self.publisher = None
        self.subscriber = None

    def run(self):
        self.subscriber.run()

    def __repr__(self):
        return f'Proxy "{self.name} for "{self.url}"'
