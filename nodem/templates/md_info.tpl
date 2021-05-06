### Brokers{% for broker_data in brokers_data %}
    {{ broker_data.name }}:
        transport type: {{ broker_data.type }}
        topics: {% for in_topic in broker_data.in_topics %}
            <- {{ in_topic }}{% endfor %}{% for out_topic in broker_data.out_topics %}
            -> {{ out_topic }}{% endfor %}
        rpc names:{% for rpc_service in broker_data.rpc_services %}
            + {{ rpc_service }}{% endfor %}{% for rpc_client in broker_data.rpc_clients %}
            - {{ rpc_client }}{% endfor %}
    {% endfor %}

### Unused Publishers{% for unpub in unused_publishers %}
- {{ unpub.topic }} {% if unpub.data_model %}
```
{ {% for value, type in unpub.data_model.items() %}
    "{{ value }}": {{ type }}{% endfor %}
}
```{% endif %}
{% endfor %}

### Unused Subscribers{% for topic in unused_subscribers %}
- {{ topic }}{% endfor %}


### Unused RPC Services{% for urpcs in unused_rpc_services %}
- {{ urpcs.name }}
```
{ {% for value, type in urpcs.data_model.items() %}
    "{{ value }}": {{ type }} {% endfor %}
}
```
{% endfor %}

### Unused RPC Clients{% for urpcc in unused_rpc_clients %}
- {{ urpcc.name }}
```
{ {% for value, type in urpcc.data_model.items() %}
    "{{ value }}": {{ type }} {% endfor %}
}
```
{% endfor %}


### Proxies {% for proxy in proxies %}
- {{ proxy.name }}: {{ proxy.method }} {{ proxy.url }}
{% endfor %}