from commlib.msg import RPCMessage, DataClass
from nodem.definitions import RPC_MESSAGES_PATH

RPC_FIELD_TEMPLATE = """        {{ name }}: {{ type }}"""
RPC_DEF_FIELD_TEMPLATE = """        {{ name }}: {{ type }} = {{ value }}"""

RPC_MESSAGE_TEMPLATE = """

class {{ name }}(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
{{ req_fields }}

    @DataClass
    class Response(RPCMessage.Response):
{{ resp_fields }}
"""


def add_rpc_message(name, properties, method):
    full_template = RPC_MESSAGE_TEMPLATE
    # replace name
    full_template = full_template.replace('{{ name }}', name)
    resp_fields_template = ''

    for pproperty in properties:
        if pproperty.default:
            field_template = RPC_DEF_FIELD_TEMPLATE
        else:
            field_template = RPC_FIELD_TEMPLATE
        field_template = field_template.replace('{{ name }}', pproperty.name)
        field_template = field_template.replace('{{ type }}', str(pproperty.type))
        field_template = field_template.replace('{{ value }}',
                                                str(pproperty.default))

        resp_fields_template += f'{field_template}\n'

    # replace fields to main tempalte
    if method == 'response':
        full_template = full_template.replace('{{ resp_fields }}',
                                              resp_fields_template)
        full_template = full_template.replace('{{ req_fields }}', '        pass')
    else:
        full_template = full_template.replace('{{ req_fields }}',
                                              resp_fields_template)
        full_template = full_template.replace('{{ resp_fields }}', '        pass')

    with open(RPC_MESSAGES_PATH, 'a') as f:
        f.write(full_template)


class AddTwoIntMessage(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
        a: int = 0
        b: int = 0

    @DataClass
    class Response(RPCMessage.Response):
        c: int = 0


def default_on_message(msg):
    print(type(msg))
    print(f'Message: {msg}')
