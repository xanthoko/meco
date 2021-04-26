from nodem.parser import NodesHandler

example_model_path = '../examples/models/simple.ent'
node_parser = NodesHandler(example_model_path)


def get_out_node():
    return node_parser.get_node_by_name('thermoSensor', 'out')


def get_in_node():
    return node_parser.get_node_by_name('ACDevice', 'in')


# ----- PubSub -----
example_subscriber = get_in_node().subscribers[0]
example_subscriber.run()

example_publisher = get_out_node().publishers[0]

# ----- RPC -----
example_rpc_service = get_in_node().rpc_services[0]
example_rpc_service.run()

example_rpc_client = get_out_node().rpc_clients[0]
request = example_rpc_client.message_module().Request()
