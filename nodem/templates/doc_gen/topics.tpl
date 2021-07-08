@startuml
allow_mixing
{% for topic in topics %}
interface "{{ topic }}"{% endfor %}

{% for pub_name in pub_names %}
node {{ pub_name }}{% endfor %}

{% for sub_name in sub_names %}
node {{ sub_name }}{% endfor %}

{% for pub_topic, pubs in pub_topics.items() %}{% for pub in pubs%}
{{ pub }} -> "{{ pub_topic }}"{% endfor %}{% endfor %}

{% for sub_topic, subs in sub_topics.items() %}{% for sub in subs%}
"{{ sub_topic }}" -> {{ sub }}{% endfor %}{% endfor %}

@enduml