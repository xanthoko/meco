from commlib.node import Node as CommNode
from commlib.endpoints import TransportType
from commlib.msg import PubSubMessage, RPCMessage
from nodem.logic import default_on_message, default_on_request
from commlib.bridges import (TopicBridge as CommTopBridge, TopicBridgeType,
                             RPCBridge as CommRPCBridge, RPCBridgeType)


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


class InNode:
    def __init__(self, name: str, broker: Broker):
        self.name = name
        self.broker = broker
        self.commlib_node = self._create_commlib_node(name, broker)

        self.subscribers = []
        self.rpc_services = []

    def _create_commlib_node(self, name: str, broker: Broker) -> CommNode:
        return CommNode(node_name=name,
                        transport_type=broker.transport_type,
                        transport_connection_params=broker.connection_params,
                        debug=True)

    def __repr__(self):
        return f'InNode: {self.name}'


class OutNode:
    def __init__(self, name: str, broker: Broker):
        self.name = name
        self.broker = broker
        self.commlib_node = self._create_commlib_node(name, broker)

        self.publishers = []
        self.rpc_clients = []

    def _create_commlib_node(self, name: str, broker: Broker) -> CommNode:
        return CommNode(node_name=name,
                        transport_type=broker.transport_type,
                        transport_connection_params=broker.connection_params,
                        debug=True)

    def __repr__(self):
        return f'OutNode: {self.name}'


class Publisher:
    def __init__(self, node: OutNode, topic: str, message_class: PubSubMessage):
        self.node = node
        self.topic = topic
        self.message_class = message_class
        self.commlib_publisher = self._create_commlib_publisher(
            topic, message_class, node.commlib_node)

    def publish(self):
        if self.commlib_publisher:
            msg = self.message_class()
            self.commlib_publisher.publish(msg)
        else:
            print('[ERROR] Commlib publisher not set.')

    def _create_commlib_publisher(self, topic: str, message_module,
                                  commlib_node: CommNode):
        return commlib_node.create_publisher(topic=topic, msg_type=message_module)

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node: InNode, topic: str):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = self._create_commlib_subscriber(
            topic, node.commlib_node)

    def _create_commlib_subscriber(self, topic: str, commlib_node: CommNode):
        return commlib_node.create_subscriber(topic=topic,
                                              on_message=default_on_message)

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self, node: InNode, name: str, message_class: RPCMessage,
                 on_request):
        self.node = node
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
        return f'RPC Service of {self.node}'


class RPC_Client:
    def __init__(self, node: OutNode, name: str, message_module: RPCMessage):
        self.node = node
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
        return f'RPC Client of {self.node}'


class TopicBridge:
    def __init__(self, name: str, brokerA: Broker, brokerB: Broker, from_topic: str,
                 to_topic: str):
        self.name = name
        self.brokerA = brokerA
        self.brokerB = brokerB
        self.from_topic = from_topic
        self.to_topic = to_topic

        self.commlib_bridge = self._create_commlib_bridge()

    def _create_commlib_bridge(self):
        bridge_type = getattr(TopicBridgeType,
                              f'{self.brokerA.type}_TO_{self.brokerB.type}')

        return CommTopBridge(bridge_type,
                             from_uri=self.from_topic,
                             to_uri=self.to_topic,
                             from_broker_params=self.brokerA.connection_params,
                             to_broker_params=self.brokerB.connection_params)

    def __repr__(self):
        return f'Topic bridge {self.brokerA}-{self.brokerB}'


class RPCBridge:
    def __init__(self, name: str, brokerA: Broker, brokerB: Broker, nameA: str,
                 nameB: str):
        self.name = name
        self.brokerA = brokerA
        self.brokerB = brokerB
        self.nameA = nameA
        self.nameB = nameB

        self.commlib_bridge = self._create_commlib_bridge()

    def _create_commlib_bridge(self):
        bridge_type = getattr(RPCBridgeType,
                              f'{self.brokerA.type}_TO_{self.brokerB.type}')

        return CommRPCBridge(bridge_type,
                             from_uri=self.nameA,
                             to_uri=self.nameB,
                             from_broker_params=self.brokerA.connection_params,
                             to_broker_params=self.brokerB.connection_params)

    def __repr__(self):
        return f'RPC bridge {self.brokerA}-{self.brokerB}'
