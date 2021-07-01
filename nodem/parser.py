import os
import requests
from importlib import import_module
from json.decoder import JSONDecodeError

from commlib.node import TransportType
from comm_idl.generator import GeneratorCommlibPy
from commlib.msg import PubSubMessage, RPCMessage
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)

from nodem.logic import ReturnProxyMessage
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH
from nodem.entities import (Broker, Publisher, Subscriber, RPC_Service, RPC_Client,
                            Proxy, Node, TopicBridge, RPCBridge)
from nodem.utils import build_model, get_first, find_class_objects, typecasted_value


class EntitiesHandler:
    def __init__(self, model_path='models/nodes.ent', messages_path=None):
        # services lists
        self.default_broker = None
        self.brokers = []
        self.nodes = []
        self.topic_bridges = []
        self.rpc_bridges = []
        self.proxies = []
        # endpoints lists
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []
        # paths
        self.model_path = model_path
        self.messages_path = messages_path or MESSAGES_MODEL_PATH

        self.model = build_model(model_path)
        self.parse_model()

    def parse_model(self):
        self.parse_broker_connections()
        self.generate_message_modules()
        self.parse_nodes()
        self.parse_topic_bridges()
        self.parse_rpc_bridges()
        self.parse_proxies()

    def parse_broker_connections(self):
        """Parses the broker models and creates Broker entities with their
        connection parameters."""
        # broker_type: [
        #   transport_type: enum,
        #   connection_params: class,
        #   credentials: class
        # ]
        broker_type_map = {
            'RedisBroker': [TransportType.REDIS, redisParams, redisCreds],
            'AMQPBrokerGeneric': [TransportType.AMQP, amqpParams, amqpCreds],
            'RabbitBroker': [TransportType.AMQP, amqpParams, amqpCreds],
            'MQTTBrokerGeneric': [TransportType.MQTT, mqttParams, mqttCreds],
            'EMQXBroker': [TransportType.MQTT, mqttParams, mqttCreds]
        }

        broker_models = self.model.brokers
        for broker_model in broker_models:
            broker_model = broker_model.broker
            broker_type = broker_model.__class__.__name__

            transport_type, connection_param_class, creds_class = broker_type_map[
                broker_type]
            # retrieve connection variables from broker model
            host = broker_model.host
            port = broker_model.port
            # vhosts = broker_model.vhosts
            # vhost = vhosts[0] if vhosts else '/'
            # check if there are any credentials
            if broker_model.users:
                creds_model = broker_model.users[
                    0]  # get the first pair of credentials
                creds = creds_class(username=creds_model.username,
                                    password=creds_model.password)
            else:
                creds = None
            connection_params = connection_param_class(host, port, creds=creds)

            broker = Broker(broker_model.name, connection_params, transport_type)
            self.brokers.append(broker)

            # the grammar defines that at least one broker must be declared
            if self.default_broker is None:
                self.default_broker = self.brokers[
                    0]  # set the first broker as default

    def generate_message_modules(self):
        generator = GeneratorCommlibPy()
        generator.generate(self.messages_path, out_dir=ROOT_PATH)
        # NOTE: the out dir of messages path is determined by the name of
        # the package in messages.idl. For simplicity sake we make the assumption
        # that every package will be named msgs
        # fix import issues
        objects_messages_path = MESSAGES_DIR_PATH + '/object.py'
        if not os.path.exists(objects_messages_path):
            # pubsub and rpc message files import object file so if there
            # are no objects declared in messages.idl file, we must create
            # an empty 'object.py' file
            with open(objects_messages_path, 'w'):
                pass

        pubsub_messages_path = MESSAGES_DIR_PATH + '/pubsub.py'
        if os.path.exists(pubsub_messages_path):
            self._replace_object_imports(pubsub_messages_path)
        rpc_messages_path = MESSAGES_DIR_PATH + '/rpc.py'
        if os.path.exists(rpc_messages_path):
            self._replace_object_imports(rpc_messages_path)

    def _replace_object_imports(self, path: str):
        """The comm-idl generator has dynamic imports that need to be replaced
        by static ones."""
        with open(path, 'r+') as f:
            text = f.read()
            text = text.replace(' .object', ' nodem.msgs.object')
            f.seek(0)
            f.write(text)

    def parse_nodes(self):
        """For each InNode model creates the Node, its subscribers and its rpc
        clients."""
        node_models = find_class_objects(self.model.nodes, 'Node')

        for node_model in node_models:
            if node_model.broker:
                broker = get_first(self.brokers, 'name', node_model.broker.name)
            else:
                broker = self.default_broker
            # --- node ---
            node = Node(node_model.name, broker)
            self.nodes.append(node)

            # --- subscribers ---
            subscriber_models = find_class_objects(node_model.inports, 'Subscriber')
            self._create_subscribers_for_node(subscriber_models, node)

            # --- rpc_services ---
            rpc_service_models = find_class_objects(node_model.inports,
                                                    'RPC_Service')
            self._create_rpc_services_for_node(rpc_service_models, node)

            # --- publishers ---
            publisher_models = find_class_objects(node_model.outports, 'Publisher')
            self._create_publishers_for_node(publisher_models, node)

            # --- rpc_clients ---
            rpc_client_models = find_class_objects(node_model.outports,
                                                   'RPC_Client')
            self._create_rpc_clients_for_node(rpc_client_models, node)

    def _create_subscribers_for_node(self, subscriber_models, node: Node):
        for subscriber_model in subscriber_models:
            subscriber = self._create_subscriber_entity(subscriber_model, node)
            node.subscribers.append(subscriber)

    def _create_rpc_services_for_node(self, rpc_service_models, node: Node):
        for rpc_service_model in rpc_service_models:
            rpc_service = self._create_rpc_service_entity(rpc_service_model, node)
            node.rpc_services.append(rpc_service)

    def _create_publishers_for_node(self, publisher_models, node: Node):
        for publisher_model in publisher_models:
            publisher = self._create_publisher_entity(publisher_model, node)
            node.publishers.append(publisher)

    def _create_rpc_clients_for_node(self, rpc_client_models, node: Node):
        try:
            rpc_msg_module = import_module('nodem.msgs.rpc')
        except ModuleNotFoundError:
            # no rpc message found -> no rpc clients
            pass
        for rpc_client_model in rpc_client_models:
            message_module = getattr(rpc_msg_module, rpc_client_model.object.name)
            rpc_client = RPC_Client(node, rpc_client_model.name, message_module,
                                    rpc_client_model.frequency,
                                    rpc_client_model.mock)

            node.rpc_clients.append(rpc_client)
            self.rpc_clients.append(rpc_client)

    def _create_publisher_entity(self, publisher_model, parent):
        msg_module = import_module('nodem.msgs.pubsub')
        topic = publisher_model.topic
        frequency = publisher_model.frequency
        mock = publisher_model.mock
        # message class is an attribute of message module
        try:
            pubsub_message = getattr(msg_module, publisher_model.object.name)
        except AttributeError:
            pubsub_message = PubSubMessage

        publisher = Publisher(parent, topic, pubsub_message, frequency, mock)
        self.publishers.append(publisher)
        return publisher

    def _create_subscriber_entity(self, subscriber_model, parent, on_message=None):
        topic = subscriber_model.topic

        def custom_on_message(msg, topic=topic):
            print(f'-----\nMessage consumed.\nTopic: "{topic}"\nMsg: {msg}')
            return msg

        on_message = on_message or custom_on_message
        subscriber = Subscriber(parent, topic, on_message)
        self.subscribers.append(subscriber)
        return subscriber

    def _create_rpc_service_entity(self,
                                   rpc_service_model,
                                   parent,
                                   on_request=None,
                                   rpc_message=None):
        rpc_msg_module = import_module('nodem.msgs.rpc')

        name = rpc_service_model.name
        # message classes are attributes of the rpc_msg module
        if not rpc_message:
            try:
                rpc_message = getattr(rpc_msg_module, rpc_service_model.object.name)
            except AttributeError:
                rpc_message = RPCMessage

        def custom_on_request(msg):
            print(f'<-----\nRequest received.\nName: "{name}."')
            return rpc_message.Response()

        on_request = on_request or custom_on_request
        rpc_service = RPC_Service(parent, name, rpc_message, on_request)

        self.rpc_services.append(rpc_service)
        return rpc_service

    def parse_topic_bridges(self):
        """A topic bridge connects BrokerA(from_topic) -> BrokerB(to_topic)"""
        topic_bridge_models = find_class_objects(self.model.bridges, 'TopicBridge')

        for topic_bridge_model in topic_bridge_models:
            name = topic_bridge_model.name
            brokerA = self.get_broker_by_name(topic_bridge_model.brokerA.name)
            brokerB = self.get_broker_by_name(topic_bridge_model.brokerB.name)
            from_topic = topic_bridge_model.fromTopic
            to_topic = topic_bridge_model.toTopic

            bridge = TopicBridge(name=name,
                                 brokerA=brokerA,
                                 brokerB=brokerB,
                                 from_topic=from_topic,
                                 to_topic=to_topic)
            self.topic_bridges.append(bridge)

    def parse_rpc_bridges(self):
        """An rpc bridge connects BrokerA(nameA) -> BrokerB(nameB)"""
        rpc_bridge_models = find_class_objects(self.model.bridges, 'RPCBridge')

        for rpc_bridge_model in rpc_bridge_models:
            name = rpc_bridge_model.name
            brokerA = self.get_broker_by_name(rpc_bridge_model.brokerA.name)
            brokerB = self.get_broker_by_name(rpc_bridge_model.brokerB.name)
            nameA = rpc_bridge_model.nameA
            nameB = rpc_bridge_model.nameB

            bridge = RPCBridge(name=name,
                               brokerA=brokerA,
                               brokerB=brokerB,
                               nameA=nameA,
                               nameB=nameB)
            self.rpc_bridges.append(bridge)

    def parse_proxies(self):
        """A proxy makes a request to the given url and returns the response
        as an rpc service."""
        proxy_models = find_class_objects(self.model.proxies, 'Proxy')

        for proxy_model in proxy_models:
            if proxy_model.broker:
                broker = get_first(self.brokers, 'name', proxy_model.broker.name)
            else:
                broker = self.default_broker
            name = proxy_model.name
            url = proxy_model.url
            method = proxy_model.method

            proxy = Proxy(name, url, method, broker)
            self.proxies.append(proxy)

            def make_request(msg, method=method, url=url):
                if method.upper() == 'GET':
                    resp = requests.get(url)
                elif method.upper() == 'POST':
                    if body_model := proxy_model.body:
                        data = {
                            x.name: typecasted_value(x)
                            for x in body_model.properties
                        }
                    else:
                        data = {}
                    # TODO: test in a "real" API
                    resp = requests.post(url, data=data)

                if status_code := resp.status_code != 200:
                    print(f'[ERROR] Response was {status_code}')
                    return

                try:
                    resp_msg_data = resp.json()
                except JSONDecodeError:
                    resp_msg_data = resp.text
                return ReturnProxyMessage.Response(data=resp_msg_data)

            rpc_service = self._create_rpc_service_entity(proxy_model.port, proxy,
                                                          make_request,
                                                          ReturnProxyMessage)
            proxy.rpc_service = rpc_service

    def get_node_by_name(self, node_name: str):
        return get_first(self.nodes, 'name', node_name)

    def get_broker_by_name(self, broker_name: str) -> Broker:
        return get_first(self.brokers, 'name', broker_name)

    def get_bridge_by_name(self, bridge_name: str, bridge_type: str):
        bridges = self.topic_bridges if bridge_type == 'topic' else self.rpc_bridges
        return get_first(bridges, 'name', bridge_name)

    def get_proxy_by_name(self, proxy_name: str) -> Proxy:
        return get_first(self.proxies, 'name', proxy_name)

    def get_publisher_by_topic(self, topic):
        return get_first(self.publishers, 'topic', topic)

    def get_rpc_by_name(self, name, rpc_type):
        if rpc_type == 'service':
            return get_first(self.rpc_services, 'name', name)
        else:
            return get_first(self.rpc_clients, 'name', name)
