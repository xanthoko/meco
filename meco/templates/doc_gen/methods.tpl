from meco.msgs.rpc import *

{% for message_name in message_names %}
def {{ message_name }}_on_request(msg):
    print('Got a request')
    return {{ message_name }}.Response()

{% endfor %}