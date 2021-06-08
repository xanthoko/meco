import os

from nodem.parser import NodesHandler
from nodem.definitions import ROOT_PATH

messages_path = 'examples/models/sh_messages.idl'
root_root = '/'.join(ROOT_PATH.split('/')[:-1])
example_message_path = os.path.join(root_root, messages_path)

node_parser = NodesHandler('../examples/models/smart_home.ent',
                           example_message_path)

# publishers
p1 = node_parser.get_node_by_name('temperaturePublisher').publishers[0]
p2 = node_parser.get_node_by_name('temperaturePublisher').publishers[1]
p3 = node_parser.get_node_by_name('humidityPublisher').publishers[0]
p4 = node_parser.get_node_by_name('intruderPublisher').publishers[0]
p5 = node_parser.get_node_by_name('robotPublisher').publishers[0]
# services
s1 = node_parser.get_node_by_name('RelayService').rpc_services[0]
s1.run()
# bridges
b1 = node_parser.get_bridge_by_name('RobotR4A2MyRabbit', 'topic')
b1.run()

# validation
n = node_parser.get_node_by_name('Validation')
n.run_subscribers()
c1 = n.rpc_clients[0]
msg1 = c1.message_module().Request()
