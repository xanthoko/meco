from typing import List
from jinja2 import Environment, FileSystemLoader
from importlib import import_module

from commlib.msg import RPCMessage, DataClass, DataField, Object
from nodem.definitions import TEMPLATES_DIR_PATH, MESSAGES_DIR_PATH


@DataClass
class ProxyResp(Object):
    """ProxyResp class implementation.
    """
    data: int = DataField(default=0)


@DataClass
class Header(Object):
    """Header class implementation.
    """
    timestamp: int = DataField(default=0)
    id: int = DataField(default=0)


class ReturnProxyMessage(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
        data: int
        header: int

    @DataClass
    class Response(RPCMessage.Response):
        data: ProxyResp = DataField(default=ProxyResp())
        header: Header = DataField(default=Header())


def default_on_message(msg):
    print(f'Message: {msg}')


def default_on_request(msg):
    print('Got a request')
    return msg


def generate_on_request_methods_file(message_names: List[str]) -> dict:
    file_loader = FileSystemLoader(TEMPLATES_DIR_PATH)
    env = Environment(loader=file_loader)

    template = env.get_template('methods.tpl')
    output = template.render(message_names=message_names)
    path = MESSAGES_DIR_PATH + '/methods.py'
    with open(path, 'w') as f:
        f.write(output)

    module = import_module('nodem.msgs.methods')
    return {x: getattr(module, f'{x}_on_request') for x in message_names}
