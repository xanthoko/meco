from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            json.dumps({
                'method': self.command,
                'path': self.path,
                'real_path': parsed_path.query,
                'query': parsed_path.query,
                'request_version': self.request_version,
                'protocol_version': self.protocol_version
            }).encode())
        return


if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print('Starting server at http://localhost:8000')
    server.serve_forever()

# def parse_proxies(self):
#     """A proxy makes a GET request to the given url and publishes the
#     response."""
#     proxy_models = find_class_objects(self.model.nodes, 'Proxy')

#     for proxy_model in proxy_models:
#         name = proxy_model.name
#         url = proxy_model.url
#         broker = self.get_broker_by_name(proxy_model.broker.name)

#         subscriber_model = proxy_model.subscriber
#         topic = subscriber_model.topic
#         # subscriber = Subscriber(in_node, topic)

#         proxy = Proxy(name, url, broker)
#         self.proxies.append(proxy)

# class Proxy:
#     def __init__(self, name: str, url: str, broker: Broker):
#         self.name = name
#         self.url = url
#         self.broker = broker

#     def __repr__(self):
#         return f'Proxy "{self.name}" for "{self.url}"'

#     def get_proxy_by_name(self, proxy_name: str) -> Proxy:
#         return get_first(self.proxies, 'name', proxy_name)
#
