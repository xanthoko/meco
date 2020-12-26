# from traceback_with_variables import activate_by_import

from commlib.msg import RPCMessage, DataClass
from commlib.transports.amqp import ConnectionParameters
from commlib.node import TransportType, Node as CommNode

from entities import Node
from utils import get_all, build_model

transport = TransportType.AMQP
conn_params = ConnectionParameters()


def default_on_message(msg):
    print(f'Message: {msg}')


class AddTwoIntMessage(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
        a: int = 0
        b: int = 0

    @DataClass
    class Response(RPCMessage.Response):
        c: int = 0


def default_on_request(msg):
    print(f'Request Message: {msg}')
    resp = AddTwoIntMessage.Response(c=msg.a + msg.b)
    return resp


class NodesHandler:
    """Class that handles the textx model that contains "nodes" attribute."""
    def __init__(self, model_path='models/nodes.ent'):
        self.nodes = []
        # service entities lists
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.model = build_model(model_path)
        self.parse_model()

    def parse_model(self):
        self._create_node_objects()
        # NOTE: the alternative for avoiding calling _update_service_entities_lists
        # is to execute
        # return [publishers.extend(x.publishers) for x in a.nodes]
        # every time publishers list was requested. I don't think it would be better
        self._update_service_entities_lists()
        self._create_commlib_entities_for_services()

    def _create_node_objects(self):
        """Create a Node object for every node model."""
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

    def _update_service_entities_lists(self):
        """Extends the service entities lists with the created service entities of each
        node object."""
        for node in self.nodes:
            self.publishers.extend(node.publishers)
            self.subscribers.extend(node.subscribers)
            self.rpc_services.extend(node.rpc_services)
            self.rpc_clients.extend(node.rpc_clients)

    def _create_commlib_entities_for_services(self):
        self._create_commlib_nodes()
        self._create_commlib_publishers()
        self._create_commlib_subscribers()
        self._create_commlib_rpc_services()
        self._create_commlib_rpc_clients()

    def _create_commlib_nodes(self):
        for node in self.nodes:
            commlib_node = CommNode(node_name=node.name,
                                    transport_type=transport,
                                    transport_connection_params=conn_params,
                                    debug=True)
            node.commlib_node = commlib_node

    def _create_commlib_publishers(self):
        for publisher in self.publishers:
            commlib_publisher = publisher.node.commlib_node.create_publisher(
                topic=publisher.topic)
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
                msg_type=AddTwoIntMessage,
                on_request=default_on_request)
            rpc_service.commlib_rpc_service = commlib_rpc_service

    def _create_commlib_rpc_clients(self):
        for rpc_client in self.rpc_clients:
            commlib_rpc_client = rpc_client.node.commlib_node.create_rpc_client(
                rpc_name=rpc_client.name, msg_type=AddTwoIntMessage)
            rpc_client.commlib_rpc_client = commlib_rpc_client


if __name__ == '__main__':
    a = NodesHandler()
