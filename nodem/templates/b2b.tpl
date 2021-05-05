@startuml
{% for t_bridge in t_bridges %}
    hexagon {{ t_bridge.name }}
    [{{ t_bridge.brokerA }}] -> {{ t_bridge.name }}
    {{ t_bridge.name }} -> [{{ t_bridge.brokerB }}]
{% endfor %}
@enduml