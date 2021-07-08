@startuml
allow_mixing
{% if title %}
title <b>{{ title }}</b>{% endif %}

{% for broker in brokers %}
    queue {{ broker }}{% endfor %}

{% for subscriber in subscribers %}
    object {{ subscriber.topic}}
    {{ subscriber.broker }} .> {{ subscriber.topic }} {% endfor %}


{% for rpc_service in rpc_services %}
    object {{ rpc_service.name}}{ {% for name, type in rpc_service.message.items() %}
            {{ name }}: {{ type }}{% endfor %}
    }
    {{ rpc_service.broker }} .> {{ rpc_service.name }} {% endfor %}

@enduml