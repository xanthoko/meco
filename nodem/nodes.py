from commlib.node import Node as CommNode


class BaseNode:
    def __init__(self, name: str, broker):
        self.name = name
        self.broker = broker
        self.commlib_node = self._create_commlib_node()

    def _create_commlib_node(self):
        return CommNode(node_name=self.name,
                        transport_type=self.broker.transport_type,
                        transport_connection_params=self.broker.connection_params,
                        debug=True)


class InNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super(InNode, self).__init__(*args, **kwargs)

        self.subscribers = []
        self.rpc_services = []

    def __repr__(self):
        return f'InNode: {self.name}'


class OutNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super(OutNode, self).__init__(*args, **kwargs)

        self.publishers = []
        self.rpc_clients = []

    def __repr__(self):
        return f'OutNode: {self.name}'


class BiNode(BaseNode):
    def __init__(self, *args, **kwargs):
        super(BiNode, self).__init__(*args, **kwargs)

        self.subscriber = None
        self.publisher = None

    def __repr__(self):
        return f'BiNode {self.name}'
