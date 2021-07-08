import os
import argparse
from pathlib import Path
from shutil import rmtree

from comm_idl.generator import GeneratorCommlibPy

from nodem.logic import ReturnProxyMessage
from nodem.diagram_parser import _write_template_to_file
from nodem.utils import build_model, find_class_objects, typecasted_value
from nodem.definitions import (MESSAGES_MODEL_PATH, MESSAGES_DIR_PATH, ROOT_PATH,
                               CODE_OUTPUTS_DIR_PATH)


class EntitiesHandler:
    def __init__(self, model_path='models/nodes.ent', messages_path=None):
        self.model_path = model_path
        self.messages_path = messages_path or MESSAGES_MODEL_PATH

        # clear code_outputs directory
        rmtree(CODE_OUTPUTS_DIR_PATH)
        Path(CODE_OUTPUTS_DIR_PATH).mkdir(exist_ok=True)

        self.model = build_model(model_path)

    def parse_model(self):
        self.parse_broker_connections()
        self.generate_message_modules()
        self.parse_nodes()
        self.parse_topic_bridges()
        self.parse_rpc_bridges()
        self.parse_proxies()

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
        proxy_models = find_class_objects(self.model.proxies, 'RESTProxy')

        for proxy_model in proxy_models:
            name = proxy_model.name

            body_params = _get_params(proxy_model.body)
            query_params = _get_params(proxy_model.query)
            path_params = _get_params(proxy_model.path)
            header_params = _get_params(proxy_model.header)

            _write_template_to_file(
                'entities/proxy.tpl', {
                    'name': name,
                    'body_params': body_params,
                    'query_params': query_params,
                    'path_params': path_params,
                    'header_params': header_params,
                    'url': proxy_model.url,
                    'method': proxy_model.method,
                    'broker': proxy_model.broker.name,
                    'rpc_name': proxy_model.port.name,
                    'rpc_message_module': ReturnProxyMessage
                }, f'code_outputs/proxy_{name}.py')


def _get_params(properties_model):
    if properties_model:
        params = {x.name: typecasted_value(x) for x in properties_model.properties}
    else:
        params = {}
    return params


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("--model", help="Path to the meco model")
    parser.add_argument("--messages", help="Path to the message model")

    return parser.parse_args()


if __name__ == '__main__':
    cl_args = parse_args()

    default_model_path = 'models/nodes.ent'
    default_messages_path = 'models/messages.idl'

    model_path = cl_args.model or default_model_path
    messages_path = cl_args.messages or default_messages_path

    handler = EntitiesHandler(model_path=model_path, messages_path=messages_path)
    handler.parse_model()
