import requests
from importlib import import_module

from commlib.msg import PubSubMessage
from commlib.node import TransportType
from comm_idl.generator import GeneratorCommlibPy
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)

from nodem.nodes import InNode, OutNode, BiNode
from nodem.bridges import TopicBridge, RPCBridge
from nodem.logic import default_on_request, GenericDictMsg
from nodem.utils import build_model, get_first, find_class_objects
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH
from nodem.entities import (Broker, Publisher, Subscriber, RPC_Service, RPC_Client,
                            Proxy)


class NodesHandler:
    """Class that handles the textx model that contains "nodes" attribute."""
    def __init__(self, model_path='models/nodes.ent'):
        self.brokers = []
        self.in_nodes = []
        self.out_nodes = []
        self.bi_nodes = []
        self.topic_bridges = []
        self.rpc_bridges = []
        self.proxies = []
        # service entities lists
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.model = build_model(model_path)
        self.parse_model()

    def parse_model(self):
        self.parse_broker_connections()
        self.generate_message_modules()
        self.parse_in_nodes()
        self.parse_out_nodes()
        self.parse_bi_nodes()
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

        broker_models = self.model.broker
        for broker_model in broker_models:
            broker_model = broker_model.broker
            broker_type = broker_model.__class__.__name__

            transport_type, connection_param_class, creds_class = broker_type_map[
                broker_type]
            host = broker_model.host
            port = broker_model.port
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

    def generate_message_modules(self):
        generator = GeneratorCommlibPy()
        generator.generate(MESSAGES_MODEL_PATH, out_dir=ROOT_PATH)
        # fix import issues
        self._replace_object_imports(MESSAGES_DIR_PATH + '/pubsub.py')
        self._replace_object_imports(MESSAGES_DIR_PATH + '/rpc.py')

    def _replace_object_imports(self, path: str):
        """The comm-idl generator has dynamic imports that need to be replaced
        by static ones."""
        with open(path, 'r+') as f:
            text = f.read()
            text = text.replace(' .object', ' nodem.msgs.object')
            f.seek(0)
            f.write(text)

    def parse_in_nodes(self):
        """For each InNode model creates the Node, its subscribers and its rpc
        clients."""
        in_node_models = find_class_objects(self.model.nodes, 'InNode')

        for in_node_model in in_node_models:
            broker = get_first(self.brokers, 'name', in_node_model.broker.name)
            # --- node ---
            in_node = InNode(in_node_model.name, broker)
            self.in_nodes.append(in_node)

            # --- subscribers ---
            subscriber_models = find_class_objects(in_node_model.inports,
                                                   'Subscriber')
            self._create_subscribers_for_node(subscriber_models, in_node)

            # --- rpc_services ---
            rpc_service_models = find_class_objects(in_node_model.inports,
                                                    'RPC_Service')
            self._create_rpc_services_for_node(rpc_service_models, in_node)

    def _create_subscribers_for_node(self, subscriber_models, in_node: InNode):
        for subscriber_model in subscriber_models:
            subscriber = self._create_subscriber_entity(subscriber_model, in_node)
            in_node.subscribers.append(subscriber)

    def _create_rpc_services_for_node(self, rpc_service_models, in_node: InNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_service_model in rpc_service_models:
            name = rpc_service_model.name
            # message classes are attributes of the rpc_msg module
            rpc_message = getattr(rpc_msg_module, rpc_service_model.object.name)
            rpc_service = RPC_Service(in_node, name, rpc_message,
                                      default_on_request)

            in_node.rpc_services.append(rpc_service)
            self.rpc_services.append(rpc_service)

    def parse_out_nodes(self):
        """For each OutNode model creates the Node, its publishers and its rpc
        services."""
        out_node_models = find_class_objects(self.model.nodes, 'OutNode')

        for out_node_model in out_node_models:
            broker = get_first(self.brokers, 'name', out_node_model.broker.name)

            # --- node ---
            out_node = OutNode(out_node_model.name, broker)
            self.out_nodes.append(out_node)

            # --- publishers ---
            publisher_models = find_class_objects(out_node_model.outports,
                                                  'Publisher')
            self._create_publishers_for_node(publisher_models, out_node)

            # --- rpc_clients ---
            rpc_client_models = find_class_objects(out_node_model.outports,
                                                   'RPC_Client')
            self._create_rpc_clients_for_node(rpc_client_models, out_node)

    def _create_publishers_for_node(self, publisher_models, out_node: OutNode):
        for publisher_model in publisher_models:
            publisher = self._create_publisher_entity(publisher_model, out_node)
            out_node.publishers.append(publisher)

    def _create_rpc_clients_for_node(self, rpc_client_models, out_node: OutNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_client_model in rpc_client_models:
            message_module = getattr(rpc_msg_module, rpc_client_model.object.name)
            rpc_client = RPC_Client(out_node, rpc_client_model.name, message_module)

            out_node.rpc_clients.append(rpc_client)
            self.rpc_clients.append(rpc_client)

    def parse_bi_nodes(self):
        """For each BiNode models creates the Node, its publisher and its
        subscriber.

        BiNode has 1 publisher and 1 subscriber"""
        bi_node_models = find_class_objects(self.model.nodes, 'BiNode')

        for bi_node_model in bi_node_models:
            broker = get_first(self.brokers, 'name', bi_node_model.broker.name)

            # --- node ---
            bi_node = BiNode(bi_node_model.name, broker)
            self.bi_nodes.append(bi_node)

            # --- subscriber --
            subscriber_model = bi_node_model.inport
            subscriber = self._create_subscriber_entity(subscriber_model, bi_node)
            bi_node.subscriber = subscriber

            # --- publisher ---
            publisher_model = bi_node_model.outport
            publisher = self._create_publisher_entity(publisher_model, bi_node)
            bi_node.publisher = publisher

    def _create_publisher_entity(self, publisher_model, node):
        msg_module = import_module('nodem.msgs.pubsub')
        topic = publisher_model.topic
        # message class is an attribute of message module
        try:
            pubsub_message = getattr(msg_module, publisher_model.object.name)
        except AttributeError:
            pubsub_message = PubSubMessage
        publisher = Publisher(node, topic, pubsub_message)
        self.publishers.append(publisher)
        return publisher

    def _create_subscriber_entity(self, subscriber_model, node, on_message=None):
        topic = subscriber_model.topic
        subscriber = Subscriber(node, topic, on_message)
        self.subscribers.append(subscriber)
        return subscriber

    def parse_topic_bridges(self):
        """A topic bridge connects BrokerA(from_topic) -> BrokerB(to_topic)"""
        topic_bridge_models = find_class_objects(self.model.functions,
                                                 'TopicBridge')

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
        rpc_bridge_models = find_class_objects(self.model.functions, 'RPCBridge')

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
        """A proxy makes a GET request to the given url and publishes the
        response."""
        proxy_models = find_class_objects(self.model.functions, 'Proxy')

        for proxy_model in proxy_models:
            broker = get_first(self.brokers, 'name', proxy_model.broker.name)
            name = proxy_model.name
            url = proxy_model.url

            bi_node = BiNode(name, broker)
            publisher = self._create_publisher_entity(proxy_model.outport, bi_node)

            def make_get_request(msg, url=url, publisher=publisher):
                resp = requests.get(url)
                if status_code := resp.status_code != 200:
                    print(f'[ERROR] Response was {status_code}')

                generic_msg = GenericDictMsg(resp.json())
                publisher.publish(generic_msg)

            # create the bi node and endpoints
            subscriber = self._create_subscriber_entity(proxy_model.inport, bi_node,
                                                        make_get_request)
            bi_node.subscriber = subscriber
            bi_node.publisher = publisher

            # create the proxy entity
            proxy = Proxy(name, url, broker, bi_node)
            self.proxies.append(proxy)

    def get_node_by_name(self, node_name: str,
                         node_type: str) -> (InNode, OutNode, BiNode):
        if node_type == 'in':
            nodes = self.in_nodes
        elif node_type == 'out':
            nodes = self.out_nodes
        else:
            nodes = self.bi_nodes
        return get_first(nodes, 'name', node_name)

    def get_broker_by_name(self, broker_name: str) -> Broker:
        return get_first(self.brokers, 'name', broker_name)

    def get_bridge_by_name(self, bridge_name: str,
                           bridge_type: str) -> (TopicBridge, RPCBridge):
        bridges = self.topic_bridges if bridge_type == 'topic' else self.rpc_bridges
        return get_first(bridges, 'name', bridge_name)

    def get_proxy_by_name(self, proxy_name: str) -> Proxy:
        return get_first(self.proxies, 'name', proxy_name)


if __name__ == '__main__':
    a = NodesHandler()
    pext = a.get_node_by_name('Give', 'out').publishers[0]
    sext = a.get_node_by_name('Take', 'in').subscribers[0]
    sext.run()
    p = a.proxies[0]
    p.node.subscriber.run()
