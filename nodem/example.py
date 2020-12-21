import sys

from parser import NodesHandler, AddTwoIntMessage


def get_example_node_parser():
    model_path = 'models/example.ent'
    return NodesHandler(model_path)


def get_example_publisher(node_parser):
    return node_parser.nodes[0].publishers[0]


def get_example_subscriber(node_parser):
    return node_parser.nodes[-1].subscribers[0].commlib_subscriber


def get_example_rpc_service(node_parser):
    return node_parser.nodes[0].rpc_services[0].commlib_rpc_service


def get_example_rpc_client(node_parser):
    return node_parser.nodes[-1].rpc_clients[0].commlib_rpc_client


def _is_service_arg_valid(service_arg):
    valid_arguments = [
        's', 'sub', 'subscriber', 'c', 'client', 'p', 'pub', 'publisher', 'sv',
        'service'
    ]
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
    elif service_arg in ['c', 'client']:
        example_rpc_client = get_example_rpc_client(node_parser)
        msg = AddTwoIntMessage.Request(a=1, b=2)
    elif service_arg in ['p', 'pub', 'publisher']:
        example_publisher = get_example_publisher(node_parser)
    elif service_arg in ['sv', 'service']:
        example_rpc_service = get_example_rpc_service(node_parser)
        example_rpc_service.run_forever()
