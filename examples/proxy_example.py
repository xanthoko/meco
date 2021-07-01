from nodem.parser import EntitiesHandler

example_model_path = '../examples/models/proxy.ent'
example_messages_path = '../examples/models/messages.idl'
code_parser = EntitiesHandler(example_model_path, example_messages_path)
code_parser.parse_model()


def get_proxy():
    return code_parser.get_proxy_by_name('testProxy')


client = code_parser.get_node_by_name('thermoSensor').rpc_clients[0]
msg = client.message_module.Request()
proxy = get_proxy()

proxy.run()
