from meco.entities import TopicBridge, RPCBridge
from meco.code_outputs.broker_{{ brokerA }} import {{ brokerA }}
from meco.code_outputs.broker_{{ brokerB }} import {{ brokerB }}


{% if type == 'topic' %}
bridge = TopicBridge(name="{{ name }}",
                     brokerA={{ brokerA }},
                     brokerB={{ brokerB }},
                     from_topic="{{ from_topic }}",
                     to_topic="{{ to_topic }}")
{% else %}
bridge = RPCBridge(name="{{ name }}",
                   brokerA={{ brokerA }},
                   brokerB={{ brokerB }},
                   nameA="{{ from_name }}",
                   nameB="{{ to_name }}")
{% endif %}


if __name__ == '__main__':
    bridge.run()
