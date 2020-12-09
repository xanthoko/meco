from textx import metamodel_from_file
from commlib.transports.amqp import ConnectionParameters
from commlib.node import TransportType, Node as CommNode

from utils import search, get_all
from entities import Node, Connector, Subscriber

transport = TransportType.AMQP
conn_params = ConnectionParameters()


def default_on_message(msg):
    print(f'Message: {msg}')


class NodesHandler:
    def __init__(self, model_path='models/nodes.ent'):
        self.nodes = []
        self.publishers = []
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
            publishers = get_all(model_node.outports, 'type', 'publisher')
            in_subscriber = search(model_node.inports, 'type', 'subscriber')

            node_obj = Node(model_node.name, model_node.properties)
            node_obj.set_publishers(publishers)
            node_obj.set_subscriber(in_subscriber)

            self.nodes.append(node_obj)
            self.publishers.extend(node_obj.publishers)

    def _parse_connectors(self):
        model_connectors = self.model.connectors

        for model_connector in model_connectors:
            from_port = search(self.publishers, 'name',
                               model_connector.fromPort.name)

            to_node_name = model_connector.toNode.name
            to_port = model_connector.toPort
            to_node = self._get_node_obj_by_name(to_node_name)

            connector_obj = Connector(from_port, to_node, to_port)
            self._append_connector(connector_obj)

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
        for node in self.nodes:
            if node.subscriber and node.subscriber.commlib_subscriber is None:
                self._create_commlib_subscriber(node.subscriber)

    def _create_commlib_subscriber(self,
                                   subscriber,
                                   topic=None,
                                   on_message_callback=None):
        on_message = on_message_callback or default_on_message
        node = subscriber.node
        subscriber.topic = topic or subscriber.topic
        commlib_subscriber = node.commlib_node.create_subscriber(
            topic=subscriber.topic, on_message=on_message)
        subscriber.commlib_subscriber = commlib_subscriber

    def _append_connector(self, connector):
        self.connectors.append(connector)

    def _get_node_obj_by_name(self, name):
        return search(self.nodes, 'name', name)


if __name__ == '__main__':
    a = NodesHandler()
