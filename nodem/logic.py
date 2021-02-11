from nodem.utils import typecasted_value
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


def {{ mname }}(msg):
    print('Incoming Request...')
    resp = {{ name }}.Response({{ resp_vars }})
    return resp

"""


def add_rpc_message(name, method_name, properties, method):
    full_template = RPC_MESSAGE_TEMPLATE
    # replace name
    full_template = full_template.replace('{{ name }}', name)
    resp_fields_template = ''

    resp_var_str = ''
    var_props = {}
    for pproperty in properties:
        if pproperty.default:
            field_template = RPC_DEF_FIELD_TEMPLATE
        else:
            field_template = RPC_FIELD_TEMPLATE
        field_template = field_template.replace('{{ name }}', pproperty.name)
        field_template = field_template.replace('{{ type }}', str(pproperty.type))
        # TODO: check what happens if there is a default value
        field_template = field_template.replace('{{ value }}',
                                                str(pproperty.default))

        resp_fields_template += f'{field_template}\n'

        var_props[pproperty.name] = typecasted_value(pproperty)
        resp_var_str += f'{pproperty.name}={typecasted_value(pproperty)},'
    resp_var_str = resp_var_str[:-1]

    # replace the method_name
    full_template = full_template.replace('{{ mname }}', method_name)
    # replace the response variables
    full_template = full_template.replace('{{ resp_vars }}', resp_var_str)

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


def default_on_message(msg):
    print(type(msg))
    print(f'Message: {msg}')
