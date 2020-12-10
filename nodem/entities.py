from utils import typecasted_value


class Node:
    def __init__(self, name, properties, publishers, subscribers):
        self.name = name

        self._properties = []
        self.publishers = []
        self.subscribers = []

        self.set_properties(properties)
        self.set_publishers(publishers)
        self.set_subscribers(subscribers)

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
            self.publishers.append(Publisher(self, publisher.topic, payload))

    def set_subscribers(self, subscribers):
        """
        Args:
            subscribers (list of Subscriber Model)
        """
        for subscriber in subscribers:
            self.subscribers.append(Subscriber(self, subscriber.topic))

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
