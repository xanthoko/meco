from os import CLD_CONTINUED
from nodem.parser import NodesHandler

example_model_path = '../examples/models/proxy.ent'
example_messages_path = '../examples/models/messages.idl'
node_parser = NodesHandler(example_model_path, example_messages_path)


def get_proxy():
    return node_parser.get_proxy_by_name('testProxy')


client = node_parser.get_node_by_name('thermoSensor').rpc_clients[0]
msg = client.message_module.Request()
proxy = get_proxy()

proxy.run()
