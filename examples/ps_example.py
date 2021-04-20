from nodem.parser import NodesHandler
from nodem.definitions import MODELS_DIR_PATH


def get_example_node_parser():
    example_model_path = f'{MODELS_DIR_PATH}/example.ent'
    return NodesHandler(example_model_path)


def get_example_publisher(node_parser):
    return node_parser.get_node_by_name('thermoSensor', 'out').publishers[0]


def get_example_subscriber(node_parser):
    return node_parser.get_node_by_name('ACDevice',
                                        'in').subscribers[0].commlib_subscriber


def get_example_bridge(node_parser):
    if example_bridge := node_parser.get_bridge_by_name('R4A2MyRab', 'topic'):
        return example_bridge.commlib_bridge


if __name__ == '__main__':
    node_parser = get_example_node_parser()

    example_subscriber = get_example_subscriber(node_parser)
    example_subscriber.run()

    example_bridge = get_example_bridge(node_parser)
    if example_bridge:
        example_bridge.run()

    example_publisher = get_example_publisher(node_parser)
    # example_publisher.publish()
