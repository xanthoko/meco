from utils import typecasted_value


class Node:
    """The parent class that contains the service entities i.e. publishers, subscribers
    rpc_services and rpc_clients along with the given properties for the node."""
    def __init__(self, name, properties, publishers, subscribers, rpc_services,
                 rpc_clients):
        self.name = name

        self._properties = []
        self.publishers = []
        self.subscribers = []
        self.rpc_services = []
        self.rpc_clients = []

        self.set_properties(properties)
        self.set_publishers(publishers)
        self.set_subscribers(subscribers)
        self.set_rpc_services(rpc_services)
        self.set_rpc_clients(rpc_clients)

        self.commlib_node = None

    def set_properties(self, property_models):
        """
        Args:
            property_models (list of textx Property models): Each model has a
            "name", "type" and "value" attribute.
        """
        for property_model in property_models:
            setattr(self, property_model.name, typecasted_value(property_model))
            self._properties.append(property_model.name)

    def set_publishers(self, publisher_models):
        """Creates a Publisher object for every model.

        If the "object" attribute is set, the publisher's payload is set to a
        dictionary that contains the "object's" fields.

        Args:
            publisher_models (list of text Publisher models): Each model has a
                "topic" and "object" attribute.
        """
        for publisher_model in publisher_models:
            data_object = publisher_model.object  # can be None
            if data_object:
                payload = {
                    field.name: typecasted_value(field)
                    for field in data_object.fields
                }
            else:
                payload = {}
            publisher_obj = Publisher(self, publisher_model.topic, payload)
            self.publishers.append(publisher_obj)

    def set_subscribers(self, subscriber_models):
        """ Creates a Subscriber object for every model.
        Args:
            subscriber_models (list of text Subscriber models): Each model has a
                "topic" attribute.
        """
        for subscriber_model in subscriber_models:
            subscriber_obj = Subscriber(self, subscriber_model.topic)
            self.subscribers.append(subscriber_obj)

    def set_rpc_services(self, rpc_service_models):
        """ Creates an RPC_Service object for every model

        Args:
            rpc_services (list of text RPC_Service models): Each model has a
                "name" attribute.
        """
        for rpc_service_model in rpc_service_models:
            rpc_service_obj = RPC_Service(self, rpc_service_model.name)
            self.rpc_services.append(rpc_service_obj)

    def set_rpc_clients(self, rpc_client_models):
        """ Creates an RPC_Client object for every model

        Args:
            rpc_client_models (list of text RPC_Client models): Each model has a
                "name" attribute.
        """
        for rpc_client_model in rpc_client_models:
            rpc_client_obj = RPC_Client(self, rpc_client_model.name)
            self.rpc_clients.append(rpc_client_obj)

    @property
    def properties(self):
        return {x: getattr(self, x) for x in self._properties}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node, topic, payload={}):
        self.node = node
        self.topic = topic
        self.commlib_publisher = None
        self.payload = payload

    def update_payload(self, payload):
        self.payload = payload

    def publish(self):
        """Publishes the payload through commlib publisher."""
        self.commlib_publisher.publish(self.payload)

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node, topic):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self, node, name):
        self.node = node
        self.name = name
        self.commlib_rpc_service = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.node}'


class RPC_Client:
    def __init__(self, node, name):
        self.node = node
        self.name = name
        self.commlib_rpc_client = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.node}'
