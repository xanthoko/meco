from meco.entities import Broker

from commlib.node import TransportType
from commlib.transports.amqp import (ConnectionParameters as amqpParams, Credentials
                                     as amqpCreds)
from commlib.transports.mqtt import (ConnectionParameters as mqttParams, Credentials
                                     as mqttCreds)
from commlib.transports.redis import (ConnectionParameters as redisParams,
                                      Credentials as redisCreds)


broker_type_map = {
    'RedisBroker': [TransportType.REDIS, redisParams, redisCreds],
    'AMQPBrokerGeneric': [TransportType.AMQP, amqpParams, amqpCreds],
    'RabbitBroker': [TransportType.AMQP, amqpParams, amqpCreds],
    'MQTTBrokerGeneric': [TransportType.MQTT, mqttParams, mqttCreds],
    'EMQXBroker': [TransportType.MQTT, mqttParams, mqttCreds]
}
transport_type, connection_param_class, creds_class = broker_type_map["{{ broker_type }}"]
{% if username %}
creds = creds_class(username="{{ username }}", password="{{ password }}")
{% else %}
creds =  None
{% endif %}

connection_params = connection_param_class("{{ host }}", {{ port }}, creds=creds)

{{ name }} = Broker("{{name}}", connection_params, transport_type, {{ is_default }})

