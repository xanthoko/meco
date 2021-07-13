@startuml
allow_mixing
{% if title %}
title <b>{{ title }}</b>{% endif %}

{% for broker in brokers %}
    queue {{ broker }}{% endfor %}

{% for publisher in publishers %}
    object {{ publisher.topic}}{ {% for name, type in publisher.message.items() %}
            {{ name }}: {{ type }}{% endfor %}
    }
    {{ publisher.topic }} .> {{ publisher.broker }}{% endfor %}

{% for rpc_client in rpc_clients %}
    object {{ rpc_client.name}}{ {% for name, type in rpc_client.message.items() %}
            {{ name }}: {{ type }}{% endfor %}
    }
    {{ rpc_client.name }} .> {{ rpc_client.broker }}{% endfor %}

@enduml