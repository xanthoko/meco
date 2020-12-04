from textx import metamodel_from_file
from commlib.transports.amqp import ConnectionParameters
from commlib.node import TransportType, Node as CommNode

import sys

from utils import search
from entities import Node, Connector

transport = TransportType.AMQP
conn_params = ConnectionParameters()


def on_message(msg):
    print(f'Message: {msg}')


class NodesHandler:
    def __init__(self, model_path='models/nodes.ent'):
        self.nodes = []
        self.connectors = []

        metamodel = metamodel_from_file('models/grammar.tx')
        self.model = metamodel.model_from_file(model_path)

        self.parse_model()

    def parse_model(self):
        self._parse_nodes()
        self._parse_connectors()

    def _parse_nodes(self):
        model_nodes = self.model.nodes

        for model_node in model_nodes:
            properties = [{
                'name': x.name,
                'type': x.type,
                'value': x.value if x.value else None
            } for x in model_node.properties]

            out_publisher = search(model_node.outports, 'type', 'publisher')
            in_subscriber = search(model_node.inports, 'type', 'subscriber')

            node_obj = Node(model_node.name, properties)
            node_obj.set_publisher(out_publisher)
            node_obj.set_subscriber(in_subscriber)
            self._append_node(node_obj)

    def _parse_connectors(self):
        model_connectors = self.model.connectors

        for model_connector in model_connectors:
            from_node_name = model_connector.fromNode.name
            from_port = model_connector.fromPort
            from_node = self._get_node_obj_by_name(from_node_name)

            to_node_name = model_connector.toNode.name
            to_port = model_connector.toPort
            to_node = self._get_node_obj_by_name(to_node_name)

            connector_obj = Connector(from_node, from_port, to_node, to_port)
            self._append_connector(connector_obj)

    def create_commlib_nodes_and_publishers(self):
        for node in self.nodes:
            commlib_node = CommNode(node_name=node.name,
                                    transport_type=transport,
                                    transport_connection_params=conn_params,
                                    debug=True)
            node.commlib_node = commlib_node
            self._create_commlib_publisher(node, commlib_node)

    def _create_commlib_publisher(self, node, commlib_node):
        node_publisher = node.publisher
        if node_publisher:
            commlib_publisher = commlib_node.create_publisher(
                topic=node_publisher.topic)
            node_publisher.commlib_publisher = commlib_publisher

    def connect_commlib_entities(self):
        for connector in self.connectors:
            from_port = connector.from_port
            to_node = connector.to_node
            to_port = connector.to_port

            if to_port:
                connection_topic = from_port.topic
                # basically create a subscriber with the same topic as the publisher
                commlib_subscriber = to_node.commlib_node.create_subscriber(
                    topic=connection_topic, on_message=on_message)
                to_port.topic = connection_topic
                to_port.commlib_subscriber = commlib_subscriber

    def _append_node(self, node):
        self.nodes.append(node)

    def _append_connector(self, connector):
        self.connectors.append(connector)

    def _get_node_obj_by_name(self, name):
        return search(self.nodes, 'name', name)


if __name__ == '__main__':
    arguments = sys.argv[1:]

    try:
        if arguments[0] == 'test':
            model_path = 'models/example.ent'
            a = NodesHandler(model_path)
            a.create_commlib_nodes_and_publishers()
            a.connect_commlib_entities()

            service_arg = arguments[1]
            if service_arg in ['s', 'sub', 'subscriber']:
                test_subscriber = a.nodes[-1].subscriber.commlib_subscriber
                test_subscriber.run_forever()
            else:
                test_publisher = a.nodes[0].publisher
    except IndexError:
        pass
