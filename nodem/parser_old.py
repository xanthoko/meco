from importlib import import_module

from comm_idl.generator import GeneratorCommlibPy
from commlib.node import TransportType, Node as CommNode
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)

from nodem.logic import (default_on_message, default_on_request,
                         generate_on_request_methods_file)
from nodem.utils import build_model, get_first, find_class_objects
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH
from nodem.entities import (Broker, Publisher, Subscriber, RPC_Service, RPC_Client,
                            InNode, OutNode)


class NodesHandler:
    """Class that handles the textx model that contains "nodes" attribute."""
    def __init__(self, model_path='models/nodes.ent'):
        self.brokers = []
        self.in_nodes = []
        self.out_nodes = []
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
        self.create_node_objects()
        return
        self.generate_on_request_methods()
        self.create_commlib_entities_for_services()

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

    def create_node_objects(self):
        node_models = self.model.nodes
        in_node_models = find_class_objects(node_models, 'InNode')
        out_node_models = find_class_objects(node_models, 'OutNode')

        for in_node_model in in_node_models:
            subscriber_models = find_class_objects(in_node_model.inports,
                                                   'Subscriber')
            rps_services_models = find_class_objects(in_node_model.inports,
                                                     'RPC_Service')
            broker = get_first(self.brokers, 'name', in_node_model.broker.name)
            node = InNode(in_node_model.name, broker)
            self._create_subscribers_for_node(subscriber_models, node)
            self._create_rpc_services_for_node(rps_services_models, node)

            self.in_nodes.append(node)

        for out_node_model in out_node_models:
            publisher_models = find_class_objects(out_node_model.outports,
                                                  'Publisher')
            rpc_clients_models = find_class_objects(out_node_model.outports,
                                                    'RPC_Client')
            broker = get_first(self.brokers, 'name', out_node_model.broker.name)
            node = OutNode(out_node_model.name, broker)
            self._create_publishers_for_node(publisher_models, node)
            self._create_rpc_clients_for_node(rpc_clients_models, node)

            self.out_nodes.append(node)

    def _create_publishers_for_node(self, publisher_models, node: OutNode):
        pubsub_msg_module = import_module('nodem.msgs.pubsub')
        for publisher_model in publisher_models:
            pubsub_message = getattr(pubsub_msg_module, publisher_model.object.name)
            publisher = Publisher(node, publisher_model.topic, pubsub_message)

            node.publishers.append(publisher)
            self.publishers.append(publisher)

    def _create_subscribers_for_node(self, subscriber_models, node: InNode):
        for subscriber_model in subscriber_models:
            subscriber = Subscriber(node, subscriber_model.topic)

            node.subscribers.append(subscriber)
            self.subscribers.append(subscriber)

    def _create_rpc_services_for_node(self, rpc_service_models, node: InNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_service_model in rpc_service_models:
            message_name = rpc_service_model.object.name
            rpc_message = getattr(rpc_msg_module, message_name)
            rpc_service = RPC_Service(node, rpc_service_model.name, rpc_message)

            node.rpc_services.append(rpc_service)
            self.rpc_services.append(rpc_service)

    def _create_rpc_clients_for_node(self, rpc_client_models, node: OutNode):
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_client_model in rpc_client_models:
            message_name = rpc_client_model.object.name
            message_module = getattr(rpc_msg_module, message_name)
            rpc_client = RPC_Client(node, rpc_client_model.name, message_module)

            node.rpc_clients.append(rpc_client)
            self.rpc_clients.append(rpc_client)

    def generate_on_request_methods(self):
        """Creates the methods.py file that contains the on_request methods for the
        RPCMessage classes."""
        rpc_message_names = [x.message_module.__name__ for x in self.rpc_services]
        methods_dict = generate_on_request_methods_file(rpc_message_names)

        for rpc_service in self.rpc_services:
            rpc_service_name = rpc_service.message_module.__name__
            on_request_method = methods_dict.get(rpc_service_name,
                                                 default_on_request)
            rpc_service.on_request = on_request_method

    def create_commlib_entities_for_services(self):
        self._create_commlib_nodes()
        self._create_commlib_publishers()
        self._create_commlib_subscribers()
        self._create_commlib_rpc_services()
        self._create_commlib_rpc_clients()

    def _create_commlib_nodes(self):
        for node in self.in_nodes + self.out_nodes:
            commlib_node = CommNode(
                node_name=node.name,
                transport_type=node.broker.transport_type,
                transport_connection_params=node.broker.connection_params,
                debug=True)
            node.commlib_node = commlib_node

    def _create_commlib_publishers(self):
        for publisher in self.publishers:
            commlib_publisher = publisher.node.commlib_node.create_publisher(
                topic=publisher.topic, msg_type=publisher.message_module)
            publisher.commlib_publisher = commlib_publisher

    def _create_commlib_subscribers(self):
        for subscriber in self.subscribers:
            commlib_subscriber = subscriber.node.commlib_node.create_subscriber(
                topic=subscriber.topic, on_message=default_on_message)
            subscriber.commlib_subscriber = commlib_subscriber

    def _create_commlib_rpc_services(self):
        for rpc_service in self.rpc_services:
            commlib_rpc_service = rpc_service.node.commlib_node.create_rpc(
                rpc_name=rpc_service.name,
                msg_type=rpc_service.message_module,
                on_request=rpc_service.on_request)
            rpc_service.commlib_rpc_service = commlib_rpc_service

    def _create_commlib_rpc_clients(self):
        for rpc_client in self.rpc_clients:
            commlib_rpc_client = rpc_client.node.commlib_node.create_rpc_client(
                rpc_name=rpc_client.name, msg_type=rpc_client.message_module)
            rpc_client.commlib_rpc_client = commlib_rpc_client

    def get_node_by_name(self, node_name):
        total_nodes = self.in_nodes + self.out_nodes
        return get_first(total_nodes, 'name', node_name)


if __name__ == '__main__':
    a = NodesHandler()
