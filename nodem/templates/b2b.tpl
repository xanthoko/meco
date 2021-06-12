@startuml
{% if title %}
title <b>{{ title }}</b>{% endif %}

{% for bridge in bridges %}
    queue {{ bridge.brokerA }}
    queue {{ bridge.brokerB }}
    hexagon {{ bridge.name }}

    {{ bridge.brokerA }} -> {{ bridge.name }}
    {{ bridge.name }} -> {{ bridge.brokerB }}
{% endfor %}
@enduml