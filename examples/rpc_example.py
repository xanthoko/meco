import sys

from nodem.definitions import MODELS_DIR_PATH
from nodem.parser import NodesHandler, AddTwoIntMessage


def get_example_node_parser():
    example_model_path = f'{MODELS_DIR_PATH}/example.ent'
    return NodesHandler(example_model_path)


def get_example_rpc_service(node_parser):
    return node_parser.nodes[0].rpc_services[0].commlib_rpc_service


def get_example_rpc_client(node_parser):
    return node_parser.nodes[-1].rpc_clients[0].commlib_rpc_client


def _is_service_arg_valid(service_arg):
    valid_arguments = ['c', 'client', 's', 'service']
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

    if service_arg in ['c', 'client']:
        example_rpc_client = get_example_rpc_client(node_parser)
        msg = AddTwoIntMessage.Request(a=1, b=2)
    elif service_arg in ['s', 'service']:
        example_rpc_service = get_example_rpc_service(node_parser)
        example_rpc_service.run_forever()
