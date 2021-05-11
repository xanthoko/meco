from os import name
from jinja2 import Environment, FileSystemLoader

from nodem.diagram_creator import PlantUMLClient
from nodem.utils import build_model, get_first, find_class_objects
from nodem.definitions import (TEMPLATES_DIR_PATH, PLANTUML_MODELS_DIR_PATH,
                               OUTPUTS_DIR_PATH)
from nodem.diagram_entities import (Broker, Node, Subscriber, Publisher,
                                    RPC_Service, RPC_Client, TopicBridge, RPCBridge,
                                    Proxy)


class DiagramHandler:
    def __init__(self, model_path='models/nodes.ent'):
        self.diagram_creator = PlantUMLClient()
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

        self.model = build_model(model_path)
        self.parse_model()
        # outputs
        self.make_broker_connections_diagram()
        self.make_broker_to_broker_diagram()
        self.make_pubsub_routes_diagram()
        self.make_rpc_routes_diagram()
        self.make_md_file()
        self.make_routes_md_file()

    def parse_model(self):
        self.parse_brokers()
        self.parse_nodes()
        self.parse_topic_bridges()
        self.parse_rpc_bridges()
        self.parse_proxies()

    def parse_brokers(self):
        broker_type_map = {
            'RedisBroker': 'REDIS',
            'AMQPBrokerGeneric': 'AMPQ',
            'RabbitBroker': 'AMPQ',
            'MQTTBrokerGeneric': 'MQTT',
            'EMQXBroker': 'MQTT'
        }

        broker_models = self.model.brokers
        for broker_model in broker_models:
            bdsl_broker_model = broker_model.broker
            broker_type = broker_type_map.get(bdsl_broker_model.__class__.__name__,
                                              'Generic')
            broker_name = bdsl_broker_model.name
            broker = Broker(broker_name, broker_type)

            # check if current broker is the default
            if broker_model.default:
                self.default_broker = broker
            self.brokers.append(broker)

        # the grammar defines that at least one broker must be declared
        if self.default_broker is None:
            self.default_broker = self.brokers[0]  # set the first broker as default

    def parse_nodes(self):
        node_models = self.model.nodes

        for node_model in node_models:
            if node_model.broker:
                broker = get_first(self.brokers, 'name', node_model.broker.name)
            else:
                broker = self.default_broker
            # --- node ---
            node = Node(node_model.name, broker)
            self.nodes.append(node)
            broker.nodes.append(node)

            # --- endpoints ---
            self._create_subscribers_for_node(node_model, node)
            self._create_publishers_for_node(node_model, node)
            self._create_rpc_services_for_node(node_model, node)
            self._create_rpc_clients_for_node(node_model, node)

    def _create_subscribers_for_node(self, node_model, node: Node):
        subscriber_models = find_class_objects(node_model.inports, 'Subscriber')
        for subscriber_model in subscriber_models:
            subscriber = Subscriber(node, subscriber_model.topic)

            self.subscribers.append(subscriber)
            node.subscribers.append(subscriber)

    def _create_publishers_for_node(self, node_model, node: Node):
        publisher_models = find_class_objects(node_model.outports, 'Publisher')
        for publisher_model in publisher_models:
            if publisher_model.object:
                pubsub_message = {
                    x.name: x.type.name
                    for x in publisher_model.object.properties
                }
            else:
                pubsub_message = {}
            publisher = Publisher(node, publisher_model.topic, pubsub_message)

            self.publishers.append(publisher)
            node.publishers.append(publisher)

    def _create_rpc_services_for_node(self, node_model, node: Node):
        rpc_service_models = find_class_objects(node_model.inports, 'RPC_Service')
        for rpc_service_model in rpc_service_models:
            name = rpc_service_model.name
            # rpc_model -> object -> response -> data -> type -> properties
            rpc_message = {
                x.name: x.type.name
                for x in
                rpc_service_model.object.response.properties[0].type.properties
            }
            rpc_service = RPC_Service(node, name, rpc_message)

            node.rpc_services.append(rpc_service)
            self.rpc_services.append(rpc_service)

    def _create_rpc_clients_for_node(self, node_model, node: Node):
        rpc_client_models = find_class_objects(node_model.outports, 'RPC_Client')
        for rpc_client_model in rpc_client_models:
            name = rpc_client_model.name
            rpc_message = {
                x.name: x.type.name
                for x in
                rpc_client_model.object.request.properties[0].type.properties
            }
            rpc_client = RPC_Client(node, name, rpc_message)

            node.rpc_clients.append(rpc_client)
            self.rpc_clients.append(rpc_client)

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
        """A proxy makes a request to the given url and publishes the response."""
        proxy_models = find_class_objects(self.model.proxies, 'Proxy')

        for proxy_model in proxy_models:
            name = proxy_model.name
            url = proxy_model.url
            method = proxy_model.method
            if proxy_model.broker:
                broker = get_first(self.brokers, 'name', proxy_model.broker.name)
            else:
                broker = self.default_broker

            proxy = Proxy(name, url, method, broker)
            subscriber = Subscriber(proxy, proxy_model.inport.topic)
            publisher = Publisher(proxy, proxy_model.outport.topic, {})

            proxy.subscriber = subscriber
            proxy.publisher = publisher

            self.subscribers.append(subscriber)
            self.publishers.append(publisher)
            self.proxies.append(proxy)

    def get_node_by_name(self, node_name: str, node_type: str):
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

    def get_proxy_by_name(self, proxy_name: str):
        return get_first(self.proxies, 'name', proxy_name)

    def make_broker_connections_diagram(self):
        """Make diagrams with the topics and rpc names in the input and outport
        ports of each broker."""
        brokers_data = []
        broker_names = set()
        for broker in self.brokers:
            broker_names.add(broker.name)
            input_topics = [
                subscriber.topic for node in broker.nodes
                for subscriber in node.subscribers
            ]
            output_topics = [
                publisher.topic for node in broker.nodes
                for publisher in node.publishers
            ]
            rpc_clients = [
                client.name for node in broker.nodes for client in node.rpc_clients
            ]
            rpc_services = [
                server.name for node in broker.nodes for server in node.rpc_services
            ]
            broker_data = {
                'name': broker.name,
                'input_topics': input_topics,
                'output_topics': output_topics,
                'rpc_clients': rpc_clients,
                'rpc_services': rpc_services
            }
            brokers_data.append(broker_data)

        name_id = 'broker_conns'
        template_data = {'brokers_data': brokers_data, 'brokers': broker_names}
        self._create_template_file_and_diagram(name_id, template_data)

    def make_broker_to_broker_diagram(self):
        """Makes a diagram with the connections between brokers through bridges."""
        bridges_data = []
        for topic_bridge in self.topic_bridges + self.rpc_bridges:
            topic_bridge_data = {
                'name': topic_bridge.name,
                'brokerA': topic_bridge.brokerA,
                'brokerB': topic_bridge.brokerB
            }
            bridges_data.append(topic_bridge_data)

        name_id = 'b2b'
        template_data = {'bridges': bridges_data}
        self._create_template_file_and_diagram(name_id, template_data)

    def make_pubsub_routes_diagram(self):
        """Makes a diagram with the connections between nodes via topics."""
        routes_data = self.get_node_routes_via_topic()
        if not routes_data:
            return
        routes_with_nodes = []
        nodes = set()
        for route_data in routes_data:
            # each route is a dict with 'route' and 'publisher' keys
            route = route_data['route']
            topic = route_data['publisher'].topic
            message = route_data['publisher'].message_schema
            connecting_nodes = [route[0].name, route[-1].name]
            nodes.update(connecting_nodes)

            routes_with_nodes.append({
                'topic': topic,
                'nodes': connecting_nodes,
                'message': message
            })

        name_id = 'n2n_topic'
        template_data = {'routes': routes_with_nodes, 'nodes': nodes}
        self._create_template_file_and_diagram(name_id, template_data)

    def get_node_routes_via_topic(self):
        routes = []
        for publisher in self.publishers:
            # a route can start only from a node
            if not isinstance(publisher.parent, Node):
                continue

            start = [publisher.parent, publisher.parent.broker]
            continuation = self._find_continuation(publisher, publisher.topic,
                                                   publisher.parent.broker)
            route = start + continuation

            if len(route) > 2:
                route_data = {'route': route, 'publisher': publisher}
                routes.append(route_data)
        return routes

    def _find_continuation(self, element, topic: str, broker: Broker) -> list:
        # case 1: A bridge
        for bridge in self.topic_bridges:
            if bridge.brokerA == broker and bridge.from_topic == topic:
                return [bridge, bridge.brokerB] + self._find_continuation(
                    bridge, bridge.to_topic, bridge.brokerB)

        # case 2: A proxy
        for proxy in self.proxies:
            if (proxy.broker == broker and proxy.subscriber.topic == topic
                    and proxy != element):
                return [proxy] + self._find_continuation(
                    proxy, proxy.publisher.topic, broker)

        # case 3: A subscriber in the same broker
        for subscriber in self.subscribers:
            if (subscriber.topic == topic and subscriber.parent.broker == broker
                    and subscriber != element):
                return [subscriber.parent] + self._find_continuation(
                    subscriber, topic, broker)

        # no continuation found
        return []

    def make_rpc_routes_diagram(self):
        """Makes a diagram with the connections between nodes via rpc."""
        routes_data = self.get_node_routes_via_rpc()
        if not routes_data:
            return

        routes_with_nodes = []
        nodes = set()
        for route_data in routes_data:
            # each route is a dict with 'route' and 'client' keys
            route = route_data['route']
            rpc_name = route_data['client'].name
            connecting_nodes = [route[0].name, route[-1].name]
            nodes.update(connecting_nodes)

            routes_with_nodes.append({
                'rpc_name': rpc_name,
                'nodes': connecting_nodes
            })

        name_id = 'n2n_rpc'
        template_data = {'routes': routes_with_nodes, 'nodes': nodes}
        self._create_template_file_and_diagram(name_id, template_data)

    def get_node_routes_via_rpc(self):
        routes = []
        for rpc_client in self.rpc_clients:
            # a route can start only from a node
            if not isinstance(rpc_client.parent, Node):
                continue

            start = [rpc_client.parent, rpc_client.parent.broker]
            continuation = self._find_rpc_continuation(rpc_client, rpc_client.name,
                                                       rpc_client.parent.broker)
            route = start + continuation

            if len(route) > 2:
                routes.append({'route': route, 'client': rpc_client})

        return routes

    def _find_rpc_continuation(self, element, rpc_name: str, broker: Broker):
        # case 1: An rpc bridge
        for bridge in self.rpc_bridges:
            if bridge.brokerA == broker and bridge.nameA == rpc_name:
                return [bridge, bridge.brokerB] + self._find_rpc_continuation(
                    bridge, bridge.nameB, bridge.brokerB)

        # case 2: Rpc Service in the same broker
        for rpc_service in self.rpc_services:
            if (rpc_service.name == rpc_name and rpc_service.parent.broker == broker
                    and rpc_service != element):
                return [rpc_service.parent] + self._find_rpc_continuation(
                    rpc_service, rpc_name, broker)

        return []

    def make_md_file(self):
        """Creates a markdown file with the main information about the communication
        schema.

        The file contains:
            - Transport type and topics for each broker
            - Topic and data model for unused endpoints
            - Proxy data
        """
        total_in_topics = []
        total_out_topics = []
        total_rpc_services = []
        total_rpc_clients = []
        # ----- brokers -----
        brokers_data = []
        for broker in self.brokers:
            # --- topics ---
            in_topics = [
                endpoint.topic for node in broker.nodes
                for endpoint in node.subscribers
            ]
            out_topics = [
                endpoint.topic for node in broker.nodes
                for endpoint in node.publishers
            ]
            # --- rpc names ---
            rpc_services = [
                service.name for node in broker.nodes
                for service in node.rpc_services
            ]
            rpc_clients = [
                client.name for node in broker.nodes for client in node.rpc_clients
            ]
            # --- total ---
            total_in_topics += in_topics
            total_out_topics += out_topics
            total_rpc_services += rpc_services
            total_rpc_clients += rpc_clients

            broker_data = {
                'name': broker.name,
                'type': broker.transport_type,
                'in_topics': in_topics,
                'out_topics': out_topics,
                'rpc_services': rpc_services,
                'rpc_clients': rpc_clients
            }
            brokers_data.append(broker_data)

        # ----- unused -----
        unused_publishers = []
        for publisher in self.publishers:
            if (topic := publisher.topic) not in total_in_topics:
                unused_publishers.append({
                    'topic': topic,
                    'data_model': publisher.message_schema
                })
        unused_subscribers = [
            x for x in total_in_topics if x not in total_out_topics
        ]
        unused_rpc_services = []
        for rpc_service in self.rpc_services:
            if (rpc_name := rpc_service.name) not in total_rpc_clients:
                unused_rpc_services.append({
                    'name': rpc_name,
                    'data_model': rpc_service.message_schema
                })
        unused_rpc_clients = []
        for rpc_client in self.rpc_clients:
            if (rpc_name := rpc_client.name) not in total_rpc_services:
                unused_rpc_clients.append({
                    'name': rpc_name,
                    'data_model': rpc_client.message_schema
                })

        # ----- proxies -----
        proxy_data = []
        for proxy in self.proxies:
            proxy_data.append(proxy.as_dict())

        info_data = {
            'brokers_data': brokers_data,
            'unused_publishers': unused_publishers,
            'unused_subscribers': unused_subscribers,
            'unused_rpc_services': unused_rpc_services,
            'unused_rpc_clients': unused_rpc_clients,
            'proxies': proxy_data
        }
        output_path = OUTPUTS_DIR_PATH + '/info.md'
        _write_template_to_file('md_info.tpl', info_data, output_path)

    def make_routes_md_file(self):
        # TODO: make md format better
        topic_routes = self.get_node_routes_via_topic()
        topic_routes_data = []
        for topic_route in topic_routes:
            topic = topic_route['publisher'].topic
            route = topic_route['route']

            route_start = f'**{route[0].name}**({topic})'
            stations = []
            for station in route[1:-1]:
                if isinstance(station, Node):
                    stations.append(f'**{station.name}**')
                else:
                    stations.append(station.name)
            route_end = f'**{route[-1].name}**'
            topic_routes_data.append({
                'start': route_start,
                'stations': stations,
                'end': route_end,
                'topic': topic
            })

        rpc_routes = self.get_node_routes_via_rpc()
        rpc_routes_data = []
        for rpc_route in rpc_routes:
            route = rpc_route['route']
            stations = [x.name for x in route][:-1]
            route_end = route[-1].name
            rpc_routes_data.append({'stations': stations, 'end': route_end})

        output_path = OUTPUTS_DIR_PATH + '/routes.md'
        _write_template_to_file('routes.tpl', {
            'topic_routes': topic_routes_data,
            'rpc_routes': rpc_routes_data
        }, output_path)

    def _create_template_file_and_diagram(self, name_id: str, template_data: dict):
        template_name = f'{name_id}.tpl'
        output_path = OUTPUTS_DIR_PATH + f'/{name_id}.png'
        plantuml_model_path = PLANTUML_MODELS_DIR_PATH + f'/{name_id}.txt'

        _write_template_to_file(template_name, template_data, plantuml_model_path)
        self.diagram_creator.make_diagram(plantuml_model_path, output_path)


def _write_template_to_file(template_name: str, template_data: dict,
                            output_path: str):
    file_loader = FileSystemLoader(TEMPLATES_DIR_PATH)
    env = Environment(loader=file_loader)
    template = env.get_template(template_name)

    output = template.render(**template_data)
    with open(output_path, 'w') as f:
        f.write(output)


if __name__ == '__main__':
    # a = DiagramHandler('models/temp.ent')
    a = DiagramHandler()
