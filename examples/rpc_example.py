from nodem.parser import NodesHandler
from nodem.definitions import MODELS_DIR_PATH


def get_example_node_parser():
    example_model_path = f'{MODELS_DIR_PATH}/example.ent'
    return NodesHandler(example_model_path)


def get_example_rpc_service(node_parser):
    return node_parser.get_node_by_name('ACDevice', 'in').rpc_services[0]


def get_example_rpc_client(node_parser):
    return node_parser.get_node_by_name('thermoSensor', 'out').rpc_clients[0]


def get_example_bridge(node_parser):
    if example_bridge := node_parser.get_bridge_by_name('R4A2MyRab', 'rpc'):
        return example_bridge.commlib_bridge


if __name__ == '__main__':
    node_parser = get_example_node_parser()

    example_rpc_service = get_example_rpc_service(node_parser)
    example_rpc_service.commlib_rpc_service.run()

    example_bridge = get_example_bridge(node_parser)
    if example_bridge:
        example_bridge.run()

    example_rpc_client = get_example_rpc_client(node_parser)
    msg = example_rpc_client.message_module()
    request = msg.Request()

    # example_rpc_client.commlib_rpc_client.call(request)
