type_map = {'Float': float, 'Integer': int, 'Boolean': bool}


class Node:
    def __init__(self, name, properties, publisher=None, subscriber=None):
        self.name = name

        self.set_properties(properties)

        self.publisher = None
        self.subscriber = None
        self.commlib_node = None

    def set_properties(self, properties):
        """
        Args:
            properties (list of dictionaries): Each dictionary contains the name the
                value and the type of the property
        """
        for property_dict in properties:
            property_value = property_dict['value']

            if property_value is not None:
                property_type = property_dict['type']
                typecast_func = type_map[property_type]
                property_value = typecast_func(property_value)
            setattr(self, property_dict['name'], property_value)

    def set_publisher(self, publisher):
        if publisher:
            self.publisher = Publisher(self)

    def set_subscriber(self, subscriber):
        if subscriber:
            self.subscriber = Subscriber(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node):
        self.node = node
        self.topic = f'{self.node.name}.data'
        self.commlib_publisher = None

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node):
        self.node = node
        self.topic = None
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class Connector:
    def __init__(self, from_node, from_port_type, to_node, to_port_type):
        """
        Args:
            from_node (Node)
            from_port_type (string): The type of the port (publisher or rpc_service)
            to_node (Node)
            to_port_type (string): The type of the port (subscriber or rpc_client)
        """
        self.from_node = from_node
        self.from_port = getattr(from_node,
                                 from_port_type)  # Publisher or RPC_Service object
        self.to_node = to_node
        self.to_port = getattr(to_node,
                               to_port_type)  # Subscriber or RPC_Client object

    def __repr__(self):
        return f'{self.from_port} -> {self.to_port}'
