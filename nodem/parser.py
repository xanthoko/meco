# from traceback_with_variables import activate_by_import

from comm_idl.generator import GeneratorCommlibPy
from commlib.node import TransportType, Node as CommNode
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)

from nodem.entities import Node, Broker
from nodem.utils import get_all, build_model
from nodem.logic import (default_on_message, default_on_request,
                         generate_on_request_methods_file)
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH


class NodesHandler:
    """Class that handles the textx model that contains "nodes" attribute."""
    def __init__(self, model_path='models/nodes.ent'):
        self.broker = None
        self.nodes = []
        # service entities lists
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.model = build_model(model_path)
        self.parse_model()

    def parse_model(self):
        self.set_broker_connection()
        self.create_message_modules()
        self.create_node_objects()
        # NOTE: the alternative for avoiding calling _update_service_entities_lists
        # is to execute
        # return [publishers.extend(x.publishers) for x in a.nodes]
        # every time publishers list was requested. I don't think it would be better
        self.update_service_entities_lists()
        self.generate_on_request_methods()
        self.create_commlib_entities_for_services()

    def set_broker_connection(self):
        broker_model = self.model.broker.broker
        broker_type = broker_model.__class__.__name__

        broker_type_map = {
            'RedisBroker': [TransportType.REDIS, redisParams, redisCreds],
            'AMQPBrokerGeneric': [TransportType.AMQP, amqpParams, amqpCreds],
            'RabbitBroker': [TransportType.AMQP, amqpParams, amqpCreds],
            'MQTTBrokerGeneric': [TransportType.MQTT, mqttParams, mqttCreds],
            'EMQXBroker': [TransportType.MQTT, mqttParams, mqttCreds]
        }

        transport_type, connection_param_class, creds_class = broker_type_map[
            broker_type]
        host = broker_model.host
        port = broker_model.port
        # check if there are any credentials
        if broker_model.users:
            creds_model = broker_model.users[0]  # get the first pair of credentials
            creds = creds_class(username=creds_model.username,
                                password=creds_model.password)
        else:
            creds = None
        connection_params = connection_param_class(host, port, creds=creds)

        broker = Broker(connection_params, transport_type)
        self.broker = broker

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
        """Creates a Node object for every node in the model."""
        model_nodes = self.model.nodes

        for model_node in model_nodes:
            publishers = get_all(model_node.outports, '__class__.__name__',
                                 'Publisher')
            subscribers = get_all(model_node.inports, '__class__.__name__',
                                  'Subscriber')
            rpc_services = get_all(model_node.outports, '__class__.__name__',
                                   'RPC_Service')
            rpc_clients = get_all(model_node.inports, '__class__.__name__',
                                  'RPC_Client')

            node_obj = Node(model_node.name, model_node.properties, publishers,
                            subscribers, rpc_services, rpc_clients)
            self.nodes.append(node_obj)

    def update_service_entities_lists(self):
        """Extends the service entities lists with the created service entities of each
        node object."""
        for node in self.nodes:
            self.publishers.extend(node.publishers)
            self.subscribers.extend(node.subscribers)
            self.rpc_services.extend(node.rpc_services)
            self.rpc_clients.extend(node.rpc_clients)

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
        for node in self.nodes:
            commlib_node = CommNode(
                node_name=node.name,
                transport_type=self.broker.transport_type,
                transport_connection_params=self.broker.connection_params,
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


if __name__ == '__main__':
    a = NodesHandler()
