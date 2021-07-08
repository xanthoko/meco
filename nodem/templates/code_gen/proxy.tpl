from nodem.logic import ReturnProxyMessage
from nodem.entities import Proxy, RPC_Service
from nodem.code_outputs.broker_{{ broker }} import {{ broker }}


body_params = {{ body_params }}
query_params = {{ query_params }}
path_params = {{ path_params }}
header_params = {{ header_params }}

proxy = Proxy("{{ name }}", "{{ url }}", "{{ method }}", {{ broker }},
              body_params=body_params,
              query_params=query_params,
              path_params=path_params,
              header_params=header_params)

rpc_service = RPC_Service(proxy, "{{ rpc_name }}", ReturnProxyMessage, proxy.make_request)
proxy.rpc_service = rpc_service


if __name__ == '__main__':
    proxy.run()
