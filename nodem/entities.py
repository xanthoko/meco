from importlib import import_module

from commlib.msg import PubSubMessage, RPCMessage

from nodem.utils import typecasted_value


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

    def set_properties(self, object_model):
        """
        Args:
            object_model (textx Object model): Object model that has the properties
                field.
        """
        if not object_model:
            return
        node_properties = object_model.properties
        for node_property in node_properties:
            # node property has 'type', 'default' and 'name' fields
            setattr(self, node_property.name, typecasted_value(node_property))
            self._properties.append(node_property.name)

    def set_publishers(self, publisher_models):
        """Creates a Publisher object for every model.

        If the "object" attribute is set, the publisher's payload is set to a
        dictionary that contains the "object's" fields.

        Args:
            publisher_models (list of text Publisher models): Each model has a
                "topic" and "object" attribute.
        """
        pubsub_msg_module = import_module('nodem.msgs.pubsub')
        for publisher_model in publisher_models:
            if pub_object := publisher_model.object:
                pubsub_message = getattr(pubsub_msg_module, pub_object.name)
            else:
                pubsub_message = None
            publisher_obj = Publisher(self, publisher_model.topic, pubsub_message)
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
        """Creates an RPC_Service object for every model

        Args:
            rpc_services (list of text RPC_Service models): Each model has a
                "name" attribute.
        """
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_service_model in rpc_service_models:
            message_name = rpc_service_model.object.name
            rpc_message = getattr(rpc_msg_module, message_name)

            rpc_service_obj = RPC_Service(self, rpc_service_model.name, rpc_message)

            self.rpc_services.append(rpc_service_obj)

    def set_rpc_clients(self, rpc_client_models):
        """ Creates an RPC_Client object for every model

        Args:
            rpc_client_models (list of text RPC_Client models): Each model has a
                "name" attribute.
        """
        rpc_msg_module = import_module('nodem.msgs.rpc')
        for rpc_client_model in rpc_client_models:
            message_name = rpc_client_model.object.name
            message_module = getattr(rpc_msg_module, message_name)

            rpc_client_obj = RPC_Client(self, rpc_client_model.name, message_module)

            self.rpc_clients.append(rpc_client_obj)

    @property
    def properties(self):
        return {x: getattr(self, x) for x in self._properties}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Node: {self.name}'


class Publisher:
    def __init__(self, node: Node, topic: str, message_module: PubSubMessage):
        self.node = node
        self.topic = topic
        self.commlib_publisher = None
        self.message_module = message_module

    def publish(self):
        """Publishes the payload through commlib publisher."""
        if self.commlib_publisher:
            msg = self.message_module()
            self.commlib_publisher.publish(msg)
        else:
            print('[ERROR] Commlib publisher not set.')

    def __repr__(self):
        return f'Publisher of: {self.node}'


class Subscriber:
    def __init__(self, node: Node, topic: str):
        self.node = node
        self.topic = topic
        self.commlib_subscriber = None

    def __repr__(self):
        return f'Subscriber of: {self.node}'


class RPC_Service:
    def __init__(self, node: Node, name: str, message_module: RPCMessage):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.on_request = None
        self.commlib_rpc_service = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Service of {self.node}'


class RPC_Client:
    def __init__(self, node: Node, name: str, message_module: RPCMessage):
        self.node = node
        self.name = name
        self.message_module = message_module
        self.commlib_rpc_client = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'RPC Client of {self.node}'
