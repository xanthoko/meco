# The routes of connecting Nodes

## Topic Routes
{% for route in topic_routes %}{{ route.start }} --> {% for station in route.stations %}{{ station }} --> {% endfor %}{{ route.end }}

{% endfor %}

## RPC Routes
{% for route in rpc_routes %}{% for station in route.stations %}{{ station }} --> {% endfor %} {{ route.end }}
{% endfor %}