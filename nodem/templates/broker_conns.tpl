@startuml
{% for broker_data in brokers_data %}{% for input_topic in broker_data.input_topics %}
    {{ input_topic }} .> [{{ broker_data.name }}]
{% endfor %}{% for rpc_service in broker_data.rpc_services %}
    {{ rpc_service }} .> [{{ broker_data.name }}]
{% endfor %}{% for output_topic in broker_data.output_topics %}
    [{{ broker_data.name }}] .> {{ output_topic }}
{% endfor %}{% for rpc_client in broker_data.rpc_clients %}
    [{{ broker_data.name }}] .> {{ rpc_client }}
{% endfor %}{% endfor %}
@enduml