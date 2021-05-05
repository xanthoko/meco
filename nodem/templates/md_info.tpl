### Brokers{% for broker_data in brokers_data %}
    {{ broker_data.name }}:
        transport type: {{ broker_data.type }}
        topics: {% for in_topic in broker_data.in_topics %}
            <- {{ in_topic }}{% endfor %}{% for out_topic in broker_data.out_topics %}
            -> {{ out_topic }}{% endfor %}
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


### Proxies {% for proxy in proxies %}
- {{ proxy.name }}: {{ proxy.method }} {{ proxy.url }}
{% endfor %}