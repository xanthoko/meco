# The routes of connecting Nodes
Two nodes could be connected with publishers and subscribers sharing the same topic or with rpc clients and services sharing the same name.

The lists below contain the entities that connect the nodes through topics and rpc names.

## Topic Routes
{% for route in topic_routes %}- {{ route.start }} --> {% for station in route.stations %}{{ station }} --> {% endfor %}{{ route.end }}

{% endfor %}

## RPC Routes
{% for route in rpc_routes %}- {{ route.start }} --> {% for station in route.stations %}{{ station }} --> {% endfor %} {{ route.end }}

{% endfor %}