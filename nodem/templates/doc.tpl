# System Endpoints
{% for topic, data in topics.items() %}
## {{ topic }}
```
Broker: {{ data.broker }}{% if data.subscriber %}

Subscriber{% endif %}{% if data.publisher %}

Publisher:
{ {% for value, type in data.message.items() %}
    "{{ value }}": {{ type }}{% endfor %}
}{% endif %}
```
{% endfor %}