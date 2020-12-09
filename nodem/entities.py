from utils import typecasted_value
from exceptions import InvalidPortError


class Node:
    def __init__(self, name, properties, publisher=None, subscriber=None):
        self.name = name

        self._properties = []
        self.set_properties(properties)

        self.publishers = []
        self.subscriber = None
        self.commlib_node = None

    def set_properties(self, model_properties):
        """
        Args:
            properties (list of model properties): Each properties has a name, type
                and value attribute.
        """
        for model_property in model_properties:
            setattr(self, model_property.name, typecasted_value(model_property))
            self._properties.append(model_property.name)

    def set_publishers(self, publishers):
        """
        Args:
            publishers (list of Publisher Model)
        """
        for publisher in publishers:
            data_object = publisher.object
            if data_object:
                payload = {
                    field.name: typecasted_value(field)
                    for field in data_object.fields
                }
            else:
                payload = {}
            self.publishers.append(Publisher(self, publisher.name, payload))

    def set_subscriber(self, subscriber):
        if subscriber:
            self.subscriber = Subscriber(self)

    @property
    def properties(self):
        return {x: getattr(self, x) for x in self._properties}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node, name, payload={}):
        self.node = node
        self.name = name
        self.topic = f'{self.node.name}.{self.name}.data'
        self.commlib_publisher = None
        self.payload = payload

    def update_payload(self, payload):
        self.payload = payload

    def publish(self):
        self.commlib_publisher.publish(self.payload)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node):
        self.node = node
        self.topic = f'{self.node.name}.data'
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class Connector:
    def __init__(self, from_port, to_node, to_port_type):
        """
        Args:
            from_port (Model): Publisher or RPC_Service model
            to_node (Node)
            to_port_type (string): The type of the port (subscriber or rpc_client)
        """
        self.from_port = from_port
        try:
            self.to_port = getattr(to_node,
                                   to_port_type)  # Subscriber or RPC_Client object
        except AttributeError:
            raise InvalidPortError(to_node, to_port_type)

    def __repr__(self):
        return f'{self.from_port} -> {self.to_port}'
