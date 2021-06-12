## Brokers
- <-: publisher topic
- ->: subscriber topic
- \+  : rpc client
- \- : rpc service

```{% for broker_data in brokers_data %}
{{ broker_data.name }}:
    transport type: {{ broker_data.type }}{% if broker_data.in_topics or broker_data.out_topics %}
    topics: {% for in_topic in broker_data.in_topics %}
        <- {{ in_topic }}{% endfor %}{% for out_topic in broker_data.out_topics %}
        -> {{ out_topic }}{% endfor %}{% endif %} {% if broker_data.rpc_services or broker_data.rpc_clients %}
    rpc names:{% for rpc_service in broker_data.rpc_services %}
        + {{ rpc_service }}{% endfor %}{% for rpc_client in broker_data.rpc_clients %}
        - {{ rpc_client }}{% endfor %} {% endif %}
{% endfor %}```

## Unused Endpoints
Endpoints that exist in the model but do not connect to any other endpoint.

### Publishers{% for unpub in unused_publishers %}
- {{ unpub.topic }} {% if unpub.data_model %}
```
{ {% for value, type in unpub.data_model.items() %}
    "{{ value }}": {{ type }}{% endfor %}
}
```{% endif %}{% endfor %}

### Subscribers{% for topic in unused_subscribers %}
- {{ topic }}{% endfor %}

### RPC Services{% for urpcs in unused_rpc_services %}
- {{ urpcs.name }}
```
{ {% for value, type in urpcs.data_model.items() %}
    "{{ value }}": {{ type }} {% endfor %}
}
```
{% endfor %}

### RPC Clients{% for urpcc in unused_rpc_clients %}
- {{ urpcc.name }}{% if urpcc.data_model %}
```
{ {% for value, type in urpcc.data_model.items() %}
    "{{ value }}": {{ type }} {% endfor %}
}
```{% endif %}{% endfor %}


## Proxies {% for proxy in proxies %}
Information about the proxies used in the model
- {{ proxy.name }}: {{ proxy.method }} {{ proxy.url }}{% endfor %}