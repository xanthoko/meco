from nodem.parser import NodesHandler

example_model_path = '../examples/models/proxy.ent'
node_parser = NodesHandler(example_model_path)


def get_out_node():
    return node_parser.get_node_by_name('thermoSensor', 'out')


def get_in_node():
    return node_parser.get_node_by_name('ACDevice', 'in')


def get_proxy():
    return node_parser.get_proxy_by_name('testProxy')


external_publisher = get_out_node().publishers[0]
proxy = get_proxy()
external_subscriber = get_in_node().subscribers[0]

proxy.run()
external_subscriber.run()
external_publisher.publish()
