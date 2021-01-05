from commlib.msg import RPCMessage, DataClass


def default_on_message(msg):
    print(type(msg))
    print(f'Message: {msg}')


class AddTwoIntMessage(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
        a: int = 0
        b: int = 0

    @DataClass
    class Response(RPCMessage.Response):
        c: int = 0


def default_on_request(msg):
    print(f'Request Message: {msg}')
    resp = AddTwoIntMessage.Response(c=msg.a + msg.b)
    return resp
