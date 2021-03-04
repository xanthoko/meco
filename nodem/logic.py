def default_on_message(msg):
    print(f'Message: {msg}')


def default_on_request(msg):
    print('Got a request')
    print(msg)
    print(type(msg))
    return msg
