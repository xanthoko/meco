from nodem.parser import EntitiesHandler

example_model_path = '../examples/models/simple.ent'
node_parser = EntitiesHandler(example_model_path)

# ----- PubSub -----
example_subscriber = node_parser.get_node_by_name('ACDevice').subscribers[0]
example_subscriber.run()

example_publisher = node_parser.get_node_by_name('thermoSensor').publishers[0]

# ----- RPC -----
example_rpc_service = node_parser.get_node_by_name('ACDevice').rpc_services[0]
example_rpc_service.run()

example_rpc_client = node_parser.get_node_by_name('thermoSensor').rpc_clients[0]
request = example_rpc_client.message_module().Request()
