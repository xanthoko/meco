from nodem.parser import NodesHandler

example_model_path = '../examples/models/bridge.ent'
node_parser = NodesHandler(example_model_path)


def get_bridge(bridge_type):
    return node_parser.get_bridge_by_name('R4A2Redis', bridge_type)


# ----- PubSub -----
example_subscriber = node_parser.get_node_by_name('ACDevice').subscribers[0]
example_subscriber.run()

example_bridge = get_bridge('topic').run()

example_publisher = node_parser.get_node_by_name('thermoSensor').publishers[0]

# ----- RPC -----
example_rpc_service = node_parser.get_node_by_name('ACDevice').rpc_services[0]
example_rpc_service.run()

example_bridge = get_bridge('rpc').run()

example_rpc_client = node_parser.get_node_by_name('thermoSensor').rpc_clients[0]
request = example_rpc_client.message_module().Request()
