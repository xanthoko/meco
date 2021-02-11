from commlib.msg import RPCMessage, DataClass


# TODO: this must be generated dynamically
def default_on_request(msg):
    print('Incoming Request...')
    resp = thermoRPC_msg.Response(range=10, hfov=12, vfov=13, sensor_id='sid')
    return resp
