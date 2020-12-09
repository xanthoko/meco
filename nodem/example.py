import sys

from parser import NodesHandler


def get_example_node_parser():
    model_path = 'models/example.ent'
    return NodesHandler(model_path)


def get_example_publisher(node_parser):
    return node_parser.nodes[0].publishers[0]


def get_example_subscriber(node_parser):
    return node_parser.nodes[-1].subscribers[0].commlib_subscriber


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if arguments:
        service_arg = arguments[0]
    else:
        print('[ERROR] Please add the service argument...')
        exit()

    node_parser = get_example_node_parser()

    if service_arg in ['s', 'sub', 'subscriber']:
        example_subscriber = get_example_subscriber(node_parser)
        example_subscriber.run_forever()
    else:
        example_publisher = get_example_publisher(node_parser)
