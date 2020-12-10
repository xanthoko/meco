from textx import metamodel_from_file
from traceback_with_variables import activate_by_import
from commlib.transports.amqp import ConnectionParameters
from commlib.node import TransportType, Node as CommNode

from utils import get_first, get_all
from entities import Node, Connector, Subscriber

transport = TransportType.AMQP
conn_params = ConnectionParameters()


def default_on_message(msg):
    print(f'Message: {msg}')


class NodesHandler:
    def __init__(self, model_path='models/nodes.ent'):
        self.nodes = []
        self.publishers = []
        self.subscribers = []
        self.connectors = []

        metamodel = metamodel_from_file('models/grammar.tx')
        self.model = metamodel.model_from_file(model_path)

        self.parse_model()

    def parse_model(self):
        self._parse_nodes()
        self._parse_connectors()
        self._create_commlib_nodes_and_outports()
        self._connect_commlib_entities()
        self._create_rogue_commlib_subscribers()

    def _parse_nodes(self):
        model_nodes = self.model.nodes

        for model_node in model_nodes:
            publishers = get_all(model_node.outports, '__class__.__name__',
                                 'Publisher')
            subscibers = get_all(model_node.inports, '__class__.__name__',
                                 'Subscriber')

            node_obj = Node(model_node.name, model_node.properties)
            node_obj.set_publishers(publishers)
            node_obj.set_subscribers(subscibers)

            self.nodes.append(node_obj)
            self.publishers.extend(node_obj.publishers)
            self.subscribers.extend(node_obj.subscribers)

    def _parse_connectors(self):
        model_connectors = self.model.connectors

        for model_connector in model_connectors:
            from_port = get_first(self.publishers, 'name',
                                  model_connector.fromPort.name)
            to_port = get_first(self.subscribers, 'name',
                                model_connector.toPort.name)

            connector_obj = Connector(from_port, to_port)
            self.connectors.append(connector_obj)

    def _create_commlib_nodes_and_outports(self):
        for node in self.nodes:
            commlib_node = CommNode(node_name=node.name,
                                    transport_type=transport,
                                    transport_connection_params=conn_params,
                                    debug=True)
            node.commlib_node = commlib_node
            self._create_commlib_publisher(node, commlib_node)

    def _create_commlib_publisher(self, node, commlib_node):
        for node_publisher in node.publishers:
            commlib_publisher = commlib_node.create_publisher(
                topic=node_publisher.topic)
            node_publisher.commlib_publisher = commlib_publisher

    def _connect_commlib_entities(self):
        for connector in self.connectors:
            from_port = connector.from_port
            to_port = connector.to_port

            if isinstance(to_port, Subscriber):
                self._create_commlib_subscriber(to_port, from_port.topic)

    def _create_rogue_commlib_subscribers(self):
        rogue_subscribers = get_all(self.subscribers, 'commlib_subscriber', None)
        for rogue_subscriber in rogue_subscribers:
            self._create_commlib_subscriber(rogue_subscriber)

    def _create_commlib_subscriber(self,
                                   subscriber,
                                   topic=None,
                                   on_message_callback=default_on_message):
        node = subscriber.node
        subscriber.topic = topic or subscriber.topic
        commlib_subscriber = node.commlib_node.create_subscriber(
            topic=subscriber.topic, on_message=on_message_callback)
        subscriber.commlib_subscriber = commlib_subscriber


if __name__ == '__main__':
    a = NodesHandler()
