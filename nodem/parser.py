from textx import metamodel_from_file
from traceback_with_variables import activate_by_import
from commlib.transports.amqp import ConnectionParameters
from commlib.node import TransportType, Node as CommNode

from entities import Node
from utils import get_all

transport = TransportType.AMQP
conn_params = ConnectionParameters()


def default_on_message(msg):
    print(f'Message: {msg}')


class NodesHandler:
    def __init__(self, model_path='models/nodes.ent'):
        self.nodes = []
        self.publishers = []
        self.subscribers = []

        metamodel = metamodel_from_file('models/grammar.tx')
        self.model = metamodel.model_from_file(model_path)

        self.parse_model()

    def parse_model(self):
        self._parse_nodes()
        self._create_commlib_entities()

    def _parse_nodes(self):
        model_nodes = self.model.nodes

        for model_node in model_nodes:
            publishers = get_all(model_node.outports, '__class__.__name__',
                                 'Publisher')
            subscribers = get_all(model_node.inports, '__class__.__name__',
                                  'Subscriber')

            node_obj = Node(model_node.name, model_node.properties, publishers,
                            subscribers)

            self.nodes.append(node_obj)
            self.publishers.extend(node_obj.publishers)
            self.subscribers.extend(node_obj.subscribers)

    def _create_commlib_entities(self):
        for node in self.nodes:
            commlib_node = CommNode(node_name=node.name,
                                    transport_type=transport,
                                    transport_connection_params=conn_params,
                                    debug=True)
            node.commlib_node = commlib_node
            self._create_commlib_publisher(node, commlib_node)
            self._create_commlib_subscriber(node, commlib_node)

    def _create_commlib_publisher(self, node, commlib_node):
        for publisher in node.publishers:
            commlib_publisher = commlib_node.create_publisher(topic=publisher.topic)
            publisher.commlib_publisher = commlib_publisher

    def _create_commlib_subscriber(self,
                                   node,
                                   commlib_node,
                                   on_message_callback=default_on_message):
        for subscriber in node.subscribers:
            commlib_subscriber = commlib_node.create_subscriber(
                topic=subscriber.topic, on_message=on_message_callback)
            subscriber.commlib_subscriber = commlib_subscriber


if __name__ == '__main__':
    a = NodesHandler()
