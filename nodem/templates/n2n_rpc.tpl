@startuml
{% for node in nodes %}
    node {{ node }}{% endfor %}
{% for route in routes %}
    {{ route.nodes[0] }} ..> {{ route.nodes[1] }} : {{ route.rpc_name }}{% endfor %}
@enduml