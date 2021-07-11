from importlib import import_module

from commlib.msg import RPCMessage

from nodem.entities import Node, Subscriber, Publisher, RPC_Service, RPC_Client
from nodem.code_outputs.broker_{{ broker }} import {{ broker }}

{% if publishers %}
msg_module = import_module('nodem.msgs.pubsub'){% endif %}
{% if rpc_services %}
rpc_msg_module = import_module('nodem.msgs.rpc'){% endif %}
{% if rpc_clients %}
rpc_msg_module = import_module('nodem.msgs.rpc'){% endif %}

node = Node("{{ node_name }}", {{ broker }})

{% for subscriber in subscribers %}
subscriber_{{ loop.index }} = Subscriber(node, "{{ subscriber.topic }}")
node.subscribers.append(subscriber_{{ loop.index }}){% endfor %}

{% for publisher in publishers %}
pubsub_message_{{ loop.index }} = getattr(msg_module, "{{ publisher.message_module_name }}")
publisher_{{ loop.index }} = Publisher(node,
                                       topic="{{ publisher.topic }}",
                                       message_class=pubsub_message_{{ loop.index }}, frequency={{ publisher.frequency }}, mock={{ publisher.mock }}){% endfor %}

{% for rpc_service in rpc_services %}
{% if rpc_service.message_module_name %}
rpcs_message_{{ loop.index }} = getattr(rpc_msg_module, "{{ rpc_service.message_module_name }}"){% else %}
rpcs_message_{{ loop.index }} = RPCMessage{% endif %}
rpc_service_{{ loop.index }} = RPC_Service(node, "{{ rpc_service.name }}", rpcs_message_{{ loop.index }})
node.rpc_services.append(rpc_service_{{ loop.index }}){% endfor %}

{% for rpc_client in rpc_clients %}
rpcc_message_{{ loop.index }} = getattr(rpc_msg_module, "{{ rpc_client.message_module_name }}")
rpc_client_{{ loop.index }} = RPC_Client(node, "{{ rpc_client.name }}", rpcc_message_{{ loop.index }})
{% endfor %}

if __name__ == '__main__':
    # add activation methods here
    # node.run_subscribers()
    # node.run_rpcs()
    