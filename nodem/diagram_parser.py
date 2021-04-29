from nodem.utils import build_model, get_first, find_class_objects
from nodem.diagram_entities import (Broker, Node, Subscriber, Publisher,
                                    RPC_Service, RPC_Client, TopicBridge, RPCBridge,
                                    Proxy)


class NodesHandler:
    def __init__(self, model_path='models/nodes.ent'):
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
            pubsub_message = {}  # define the message model
            publisher = Publisher(node, publisher_model.topic, pubsub_message)

            self.publishers.append(publisher)
            node.publishers.append(publisher)

    def _create_rpc_services_for_node(self, node_model, node: Node):
        rpc_service_models = find_class_objects(node_model.inports, 'RPC_Service')
        for rpc_service_model in rpc_service_models:
            name = rpc_service_model.name
            rpc_service = RPC_Service(node, name, {})

            node.rpc_services.append(rpc_service)
            self.rpc_services.append(rpc_service)

    def _create_rpc_clients_for_node(self, node_model, node: Node):
        rpc_client_models = find_class_objects(node_model.outports, 'RPC_Client')
        for rpc_client_model in rpc_client_models:
            name = rpc_client_model.name
            rpc_client = RPC_Client(node, name, {})

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
            broker = get_first(self.brokers, 'name', proxy_model.broker.name)

            proxy = Proxy(name, url, method, broker)
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


if __name__ == '__main__':
    a = NodesHandler()
