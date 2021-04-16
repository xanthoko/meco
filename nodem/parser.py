from importlib import import_module

from commlib.node import TransportType
from comm_idl.generator import GeneratorCommlibPy
from commlib.bridges import TopicBridge, TopicBridgeType
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)

from nodem.logic import default_on_request
from nodem.utils import build_model, get_first, find_class_objects
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH
from nodem.entities import (Broker, Publisher, Subscriber, RPC_Service, RPC_Client,
                            InNode, OutNode, Bridge)


class NodesHandler:
    """Class that handles the textx model that contains "nodes" attribute."""
    def __init__(self, model_path='models/nodes.ent'):
        self.brokers = []
        self.in_nodes = []
        self.out_nodes = []
        self.bridges = []
        # service entities lists
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.model = build_model(model_path)
        self.parse_model()

    def parse_model(self):
        self.set_broker_connections()
        self.create_message_modules()
        self.parse_in_nodes()
        self.parse_out_nodes()
        self.parse_bridges()

    def set_broker_connections(self):
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

    def create_message_modules(self):
        generator = GeneratorCommlibPy()
        generator.generate(MESSAGES_MODEL_PATH, out_dir=ROOT_PATH)
        # fix import issues
        self._replace_object_imports(MESSAGES_DIR_PATH + '/pubsub.py')
        self._replace_object_imports(MESSAGES_DIR_PATH + '/rpc.py')

    def _replace_object_imports(self, path: str):
        with open(path, 'r+') as f:
            text = f.read()
            text = text.replace(' .object', ' nodem.msgs.object')
            f.seek(0)
            f.write(text)

    def parse_in_nodes(self):
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

    def parse_out_nodes(self):
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

    def _create_subscribers_for_node(self, subscriber_models, in_node: InNode):
        for subscriber_model in subscriber_models:
            topic = subscriber_model.topic
            subscriber = Subscriber(in_node, topic)

            in_node.subscribers.append(subscriber)
            self.subscribers.append(subscriber)

    def _create_rpc_services_for_node(self, rpc_service_models, in_node: InNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_service_model in rpc_service_models:
            name = rpc_service_model.name
            rpc_message = getattr(rpc_msg_module, rpc_service_model.object.name)
            rpc_service = RPC_Service(in_node, name, rpc_message,
                                      default_on_request)

            in_node.rpc_services.append(rpc_service)
            self.rpc_services.append(rpc_service)

    def _create_publishers_for_node(self, publisher_models, out_node: OutNode):
        pubsub_msg_module = import_module('nodem.msgs.pubsub')
        for publisher_model in publisher_models:
            topic = publisher_model.topic
            pubsub_message = getattr(pubsub_msg_module, publisher_model.object.name)
            publisher = Publisher(out_node, topic, pubsub_message)

            out_node.publishers.append(publisher)
            self.publishers.append(publisher)

    def _create_rpc_clients_for_node(self, rpc_client_models, out_node: OutNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_client_model in rpc_client_models:
            message_module = getattr(rpc_msg_module, rpc_client_model.object.name)
            rpc_client = RPC_Client(out_node, rpc_client_model.name, message_module)

            out_node.rpc_clients.append(rpc_client)
            self.rpc_clients.append(rpc_client)

    def parse_bridges(self):
        bridge_models = find_class_objects(self.model.nodes, 'Bridge')

        for bridge_model in bridge_models:
            brokerA = self.get_broker_by_name(bridge_model.brokerA.name)
            brokerB = self.get_broker_by_name(bridge_model.brokerB.name)
            from_topic = bridge_model.fromTopic
            to_topic = bridge_model.toTopic

            bridge_type = getattr(
                TopicBridgeType,
                f'{brokerA.transport_type.name}_TO_{brokerB.transport_type.name}')
            commlib_bridge = TopicBridge(
                bridge_type,
                from_uri=from_topic,
                to_uri=to_topic,
                from_broker_params=brokerA.connection_params,
                to_broker_params=brokerB.connection_params)
            bridge = Bridge(brokerA, brokerB, from_topic, to_topic, commlib_bridge)

            self.bridges.append(bridge)

    def get_node_by_name(self, node_name):
        total_nodes = self.in_nodes + self.out_nodes
        return get_first(total_nodes, 'name', node_name)

    def get_broker_by_name(self, broker_name):
        return get_first(self.brokers, 'name', broker_name)


if __name__ == '__main__':
    a = NodesHandler()
