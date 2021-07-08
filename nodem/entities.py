from time import sleep
from typing import Optional
from datetime import datetime
from random import uniform, choice, randint

from commlib.msg import PubSubMessage, RPCMessage
from commlib.node import Node as CommNode, TransportType
from commlib.bridges import (TopicBridge as CommTopBridge, TopicBridgeType,
                             RPCBridge as CommRPCBridge, RPCBridgeType)


class Broker:
    def __init__(self,
                 name: str,
                 connection_params: dict,
                 transport_type: TransportType,
                 is_default: Optional[bool] = False):
        self.name = name
        self.connection_params = connection_params
        self.transport_type = transport_type
        self.type = self.transport_type.name
        self.is_default = False

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

    def run_subscribers(self):
        for subscriber in self.subscribers:
            subscriber.run()

    def run_rpcs(self):
        for rpc_service in self.rpc_services:
            rpc_service.run()

    def _create_commlib_node(self):
        return CommNode(node_name=self.name,
                        transport_type=self.broker.transport_type,
                        transport_connection_params=self.broker.connection_params,
                        debug=True)

    def __repr__(self):
        return f'Node {self.name}'


class Publisher:
    def __init__(self,
                 parent,
                 topic: str,
                 message_class: PubSubMessage,
                 frequency: Optional[int] = None,
                 mock: Optional[bool] = False):
        self.parent = parent
        self.topic = topic
        self.message_class = message_class
        self.frequency = frequency
        self.mock = mock

        if isinstance(parent, Node):
            self.commlib_publisher = self._create_commlib_publisher(
                topic, message_class, parent.commlib_node)
        else:
            self.commlib_publisher = self._create_commlib_bare_publisher(
                topic, message_class, parent.broker)

    def publish(self):
        msg = self.message_class()
        if self.mock:
            # filling with random data
            dict_msg = self.message_class().as_dict()
            mock_value_map = {
                int: randint(0, 50),
                float: uniform(0, 1),
                bool: choice([True, False])
            }
            for key in dict_msg:
                msg_att = getattr(msg, key)
                mock_value = mock_value_map.get(type(msg_att), 'A random message')
                setattr(msg, key, mock_value)

        self.commlib_publisher.publish(msg)

    def publish_with_freq(self):
        time_interval = 1 / self.frequency if self.frequency else 1
        while True:
            self.publish()
            sleep(time_interval)

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
        on_message = on_message or self.custom_on_message
        self.commlib_subscriber = self._create_commlib_subscriber(
            topic, parent.commlib_node, on_message)

    def run(self):
        self.commlib_subscriber.run()

    def custom_on_message(self, msg, topic=None):
        topic = topic or self.topic
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print_msg = (f'-----\nMessage consumed.\nTopic: "{topic}"\nMsg: {msg}\n'
                     f'Time: {current_time}')
        print(print_msg)

        return msg

    def _create_commlib_subscriber(self, topic: str, commlib_node: CommNode,
                                   on_message):
        return commlib_node.create_subscriber(topic=topic, on_message=on_message)

    def __repr__(self):
        return f'Subscriber of: {self.parent}'


class RPC_Service:
    def __init__(self,
                 parent,
                 name: str,
                 message_class: RPCMessage,
                 on_request=None):
        self.parent = parent
        self.name = name
        self.on_request = on_request or self.custom_on_request
        self.message_class = message_class
        if isinstance(parent, Node):
            self.commlib_rpc_service = self._create_commlib_rpc_service(
                name, message_class, parent.commlib_node, self.on_request)
        else:
            self.commlib_rpc_service = self._create_commlib_bare_rpc_service(
                name, message_class, self.on_request, self.parent.broker)

    def run(self):
        self.commlib_rpc_service.run()

    def custom_on_request(self, msg):
        rpc_message = self.message_class
        name = self.name
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        print(f'<-----\nRequest received.\nName: "{name}.\nTime: {current_time}"')
        return rpc_message.Response()

    def _create_commlib_rpc_service(self, name: str, message_module, commlib_node,
                                    on_request):
        return commlib_node.create_rpc(rpc_name=name,
                                       msg_type=message_module,
                                       on_request=on_request)

    def _create_commlib_bare_rpc_service(self, rpc_name: str, message_module,
                                         on_request, broker):
        if broker.transport_type == TransportType.MQTT:
            from commlib.transports.mqtt import RPCService
        elif broker.transport_type == TransportType.AMQP:
            from commlib.transports.amqp import RPCService
        else:
            from commlib.transports.redis import RPCService
        return RPCService(rpc_name=rpc_name,
                          msg_type=message_module,
                          on_request=on_request,
                          conn_params=broker.connection_params)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.parent}'


class RPC_Client:
    def __init__(self,
                 parent,
                 name: str,
                 message_module: RPCMessage,
                 frequency: Optional[int] = None,
                 mock: Optional[bool] = False):
        self.parent = parent
        self.name = name
        self.message_module = message_module
        self.frequency = frequency
        self.mock = mock

        self.commlib_rpc_client = self._create_commlib_rpc_client(
            name, message_module, parent.commlib_node)

    def call(self, msg=None):
        msg = msg or self.message_module().Request()
        if self.mock:
            dict_msg = msg.data.as_dict()
            mock_value_map = {
                int: randint(0, 50),
                float: uniform(0, 1),
                bool: choice([True, False])
            }
            for key in dict_msg:
                msg_att = getattr(msg.data, key)
                mock_value = mock_value_map.get(type(msg_att), 'A random message')
                setattr(msg.data, key, mock_value)

        print(f'----->\nSending request.\n{msg}')
        return self.commlib_rpc_client.call(msg)

    def call_with_freq(self, msg=None):
        msg = msg or self.message_module().Request()
        time_interval = 1 / self.frequency if self.frequency else 1
        while True:
            self.call(msg)
            sleep(time_interval)

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

        self.rpc_service = None

    def run(self):
        self.rpc_service.run()

    def __repr__(self):
        return f'Proxy "{self.name} for "{self.url}"'
