import os
import requests
from json.decoder import JSONDecodeError

from comm_idl.generator import GeneratorCommlibPy

from nodem.entities import Proxy
from nodem.logic import ReturnProxyMessage
from nodem.diagram_parser import _write_template_to_file
from nodem.definitions import MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH
from nodem.utils import build_model, get_first, find_class_objects, typecasted_value


class EntitiesHandler:
    def __init__(self, model_path='models/nodes.ent', messages_path=None):
        self.model_path = model_path
        self.messages_path = messages_path or MESSAGES_MODEL_PATH

        self.model = build_model(model_path)

    def parse_model(self):
        self.parse_broker_connections()
        self.generate_message_modules()
        self.parse_nodes()
        self.parse_topic_bridges()
        self.parse_rpc_bridges()
        # self.parse_proxies()

    def parse_broker_connections(self):
        broker_models = self.model.brokers
        for broker_model in broker_models:
            is_default = broker_model.default != ''

            broker_model = broker_model.broker
            broker_type = broker_model.__class__.__name__

            data = {
                'name': broker_model.name,
                'host': broker_model.host,
                'port': broker_model.port,
                'broker_type': broker_type,
                'is_default': is_default
            }
            if broker_model.users:
                creds_model = broker_model.users[0]  # first pair of credentials
                data.update({
                    'username': creds_model.username,
                    'password': creds_model.password
                })

            _write_template_to_file('entities/broker.tpl', data,
                                    f'code_outputs/broker_{broker_model.name}.py')

    def generate_message_modules(self):
        generator = GeneratorCommlibPy()
        generator.generate(self.messages_path, out_dir=ROOT_PATH)
        # NOTE: the out dir of messages path is determined by the name of
        # the package in messages.idl. For simplicity sake we make the assumption
        # that every package will be named msgs
        # fix import issues
        objects_messages_path = MESSAGES_DIR_PATH + '/object.py'
        if not os.path.exists(objects_messages_path):
            # pubsub and rpc message files import object file so if there
            # are no objects declared in messages.idl file, we must create
            # an empty 'object.py' file
            with open(objects_messages_path, 'w'):
                pass

        pubsub_messages_path = MESSAGES_DIR_PATH + '/pubsub.py'
        if os.path.exists(pubsub_messages_path):
            self._replace_object_imports(pubsub_messages_path)
        rpc_messages_path = MESSAGES_DIR_PATH + '/rpc.py'
        if os.path.exists(rpc_messages_path):
            self._replace_object_imports(rpc_messages_path)

    def _replace_object_imports(self, path: str):
        """The comm-idl generator has dynamic imports that need to be replaced
        by static ones."""
        with open(path, 'r+') as f:
            text = f.read()
            text = text.replace(' .object', ' nodem.msgs.object')
            f.seek(0)
            f.write(text)

    def parse_nodes(self):
        node_models = find_class_objects(self.model.nodes, 'Node')

        for node_model in node_models:
            # --- node ---
            node_name = node_model.name

            # --- subscribers ---
            subscriber_models = find_class_objects(node_model.inports, 'Subscriber')
            subscribers_data = []
            for subscriber_model in subscriber_models:
                subscribers_data.append({'topic': subscriber_model.topic})

            # --- rpc_services ---
            rpc_service_models = find_class_objects(node_model.inports,
                                                    'RPC_Service')
            rpc_services_data = []
            for rpc_service_model in rpc_service_models:
                rpc_services_data.append({
                    'name':
                    rpc_service_model.name,
                    'message_module_name':
                    rpc_service_model.object.name
                })

            # --- publishers ---
            publisher_models = find_class_objects(node_model.outports, 'Publisher')
            publishers_data = []
            for publisher_model in publisher_models:
                publishers_data.append({
                    'topic':
                    publisher_model.topic,
                    'message_module_name':
                    publisher_model.object.name,
                    'frequency':
                    publisher_model.frequency,
                    'mock':
                    publisher_model.mock
                })

            # --- rpc_clients ---
            rpc_client_models = find_class_objects(node_model.outports,
                                                   'RPC_Client')
            rpc_clients_data = []
            for rpc_client_model in rpc_client_models:
                rpc_clients_data.append({
                    'name':
                    rpc_client_model.name,
                    'message_module_name':
                    rpc_client_model.object.name,
                    'frequency':
                    rpc_client_model.frequency,
                    'mock':
                    rpc_client_model.mock
                })

            _write_template_to_file(
                'entities/node.tpl', {
                    'node_name': node_name,
                    'broker': node_model.broker.name,
                    'subscribers': subscribers_data,
                    'publishers': publishers_data,
                    'rpc_services': rpc_services_data,
                    'rpc_clients': rpc_clients_data
                }, f'code_outputs/node_{node_name}.py')

    def parse_topic_bridges(self):
        """A topic bridge connects BrokerA(from_topic) -> BrokerB(to_topic)"""
        topic_bridge_models = find_class_objects(self.model.bridges, 'TopicBridge')

        for topic_bridge_model in topic_bridge_models:
            name = topic_bridge_model.name

            _write_template_to_file(
                'entities/bridge.tpl', {
                    'type': 'topic',
                    'name': name,
                    'brokerA': topic_bridge_model.brokerA.name,
                    'brokerB': topic_bridge_model.brokerB.name,
                    'from_topic': topic_bridge_model.fromTopic,
                    'to_topic': topic_bridge_model.toTopic
                }, f'code_outputs/tbridge_{name}.py')

    def parse_rpc_bridges(self):
        """An rpc bridge connects BrokerA(nameA) -> BrokerB(nameB)"""
        rpc_bridge_models = find_class_objects(self.model.bridges, 'RPCBridge')

        for rpc_bridge_model in rpc_bridge_models:
            name = rpc_bridge_model.name
            _write_template_to_file(
                'entities/bridge.tpl', {
                    'type': 'rpc',
                    'name': name,
                    'brokerA': rpc_bridge_model.brokerA.name,
                    'brokerB': rpc_bridge_model.brokerB.name,
                    'from_name': rpc_bridge_model.nameA,
                    'to_name': rpc_bridge_model.nameB
                }, f'code_outputs/rbridge_{name}.py')

    def parse_proxies(self):
        """A proxy makes a request to the given url and returns the response
        as an rpc service."""
        proxy_models = find_class_objects(self.model.proxies, 'Proxy')

        for proxy_model in proxy_models:
            if proxy_model.broker:
                broker = get_first(self.brokers, 'name', proxy_model.broker.name)
            else:
                broker = self.default_broker
            name = proxy_model.name
            url = proxy_model.url
            method = proxy_model.method

            proxy = Proxy(name, url, method, broker)
            self.proxies.append(proxy)

            def make_request(msg, method=method, url=url):
                if method.upper() == 'GET':
                    resp = requests.get(url)
                elif method.upper() == 'POST':
                    if body_model := proxy_model.body:
                        data = {
                            x.name: typecasted_value(x)
                            for x in body_model.properties
                        }
                    else:
                        data = {}
                    # TODO: test in a "real" API
                    resp = requests.post(url, data=data)

                if status_code := resp.status_code != 200:
                    print(f'[ERROR] Response was {status_code}')
                    return

                try:
                    resp_msg_data = resp.json()
                except JSONDecodeError:
                    resp_msg_data = resp.text
                return ReturnProxyMessage.Response(data=resp_msg_data)

            rpc_service = self._create_rpc_service_entity(proxy_model.port, proxy,
                                                          make_request,
                                                          ReturnProxyMessage)
            proxy.rpc_service = rpc_service


a = EntitiesHandler()
a.parse_model()
