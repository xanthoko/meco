from nodem.definitions import RPC_MESSAGES_PATH
from nodem.utils import typecasted_value

RPC_FIELD_TEMPLATE = """        {{ name }}: {{ type }} = {{ value }}"""

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


def add_rpc_message(name: str, method_name: str, properties, init: bool):
    full_template = RPC_MESSAGE_TEMPLATE
    # replace class name
    full_template = full_template.replace('{{ name }}', name)

    resp_fields_template = ''  # joined field templates
    resp_var_str = ''  # the arguments of the Response
    for pproperty in properties:
        field_template = RPC_FIELD_TEMPLATE
        prop_type = pproperty.type
        default_value = typecasted_value(pproperty) if pproperty.default else 'None'

        field_template = field_template.replace('{{ name }}', pproperty.name)
        field_template = field_template.replace('{{ type }}', str(prop_type))
        field_template = field_template.replace('{{ value }}', str(default_value))

        resp_fields_template += f'{field_template}\n'
        resp_var_str += f'{pproperty.name}={typecasted_value(pproperty)},'

    # replace the method_name
    full_template = full_template.replace('{{ mname }}', method_name)
    # replace the response variables
    resp_var_str = resp_var_str[:-1]  # remove the last \n
    full_template = full_template.replace('{{ resp_vars }}', resp_var_str)

    # replace fields to main template
    full_template = full_template.replace('{{ resp_fields }}', resp_fields_template)
    full_template = full_template.replace('{{ req_fields }}', '        pass')

    # append final template to file
    if init:
        with open(RPC_MESSAGES_PATH, 'w') as f:
            f.write('from commlib.msg import RPCMessage, DataClass\n')
            f.write(full_template)
    else:
        with open(RPC_MESSAGES_PATH, 'a') as f:
            f.write(full_template)


def default_on_message(msg):
    print(type(msg))
    print(f'Message: {msg}')
