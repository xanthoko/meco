import sys
from time import sleep

from nodem.parser import NodesHandler
from nodem.definitions import MODELS_DIR_PATH


def get_example_node_parser():
    example_model_path = f'{MODELS_DIR_PATH}/example.ent'
    return NodesHandler(example_model_path)


def get_example_publisher(node_parser):
    return node_parser.get_node_by_name('thermoSensor').publishers[0]


def get_example_subscriber(node_parser):
    return node_parser.get_node_by_name(
        'ACDevice').subscribers[0].commlib_subscriber


def _is_service_arg_valid(service_arg):
    valid_arguments = ['s', 'sub', 'subscriber', 'p', 'pub', 'publisher']
    return service_arg in valid_arguments


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if arguments:
        service_arg = arguments[0]
        if not _is_service_arg_valid(service_arg):
            print('[ERROR] Invalid service argument...')
            exit()
    else:
        print('[ERROR] Please add the service argument...')
        exit()

    node_parser = get_example_node_parser()

    if service_arg in ['s', 'sub', 'subscriber']:
        example_subscriber = get_example_subscriber(node_parser)
        example_subscriber.run_forever()
    elif service_arg in ['p', 'pub', 'publisher']:
        example_publisher = get_example_publisher(node_parser)
        example_publisher.publish()
        sleep(1)
