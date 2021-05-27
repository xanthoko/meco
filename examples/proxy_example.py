from nodem.parser import NodesHandler

example_model_path = '../examples/models/proxy.ent'
node_parser = NodesHandler(example_model_path)


def get_proxy():
    return node_parser.get_proxy_by_name('testProxy')


external_publisher = node_parser.get_node_by_name('thermoSensor').publishers[0]
proxy = get_proxy()
external_subscriber = node_parser.get_node_by_name('ACDevice').subscribers[0]

proxy.run()
external_subscriber.run()
external_publisher.publish()
