from nodem.parser import EntitiesHandler

example_model_path = '../examples/models/simple.ent'
code_parser = EntitiesHandler(example_model_path)
code_parser.parse_model()

# ----- PubSub -----
example_subscriber = code_parser.get_node_by_name('ACDevice').subscribers[0]
example_subscriber.run()

example_publisher = code_parser.get_node_by_name('thermoSensor').publishers[0]

# ----- RPC -----
example_rpc_service = code_parser.get_node_by_name('ACDevice').rpc_services[0]
example_rpc_service.run()

example_rpc_client = code_parser.get_node_by_name('thermoSensor').rpc_clients[0]
request = example_rpc_client.message_module().Request()
