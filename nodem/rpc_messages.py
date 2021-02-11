from commlib.msg import RPCMessage, DataClass


class thermoRPC_msg(RPCMessage):
    @DataClass
    class Request(RPCMessage.Request):
        pass

    @DataClass
    class Response(RPCMessage.Response):
        range: float
        hfov: float
        vfov: float
        sensor_id: str = sid



def thermoRPC_on_request(msg):
    print('Incoming Request...')
    resp = thermoRPC_msg.Response(range=None,hfov=None,vfov=None,sensor_id=sid)
    return resp

