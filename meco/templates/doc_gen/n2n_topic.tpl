@startuml
{% if title %}
title <b>{{ title }}</b>{% endif %}

{% for node in nodes %}
    node {{ node }}{% endfor %}
{% for route in routes %}
    {{ route.nodes[0] }} ..> {{ route.nodes[1] }} : {{ route.topic }}{% endfor %}
@enduml