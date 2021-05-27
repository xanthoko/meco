from commlib.node import Node as CommNode


class Node:
    def __init__(self, name: str, broker):
        self.name = name
        self.broker = broker
        self.commlib_node = self._create_commlib_node()

        self.subscribers = []
        self.rpc_services = []
        self.publishers = []
        self.rpc_clients = []

    def _create_commlib_node(self):
        return CommNode(node_name=self.name,
                        transport_type=self.broker.transport_type,
                        transport_connection_params=self.broker.connection_params,
                        debug=True)

    def __repr__(self):
        return f'Node {self.name}'
