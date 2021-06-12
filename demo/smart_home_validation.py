import os

from nodem.parser import NodesHandler
from nodem.definitions import ROOT_PARENT

messages_path = 'demo/models/sh_messages.idl'
example_message_path = os.path.join(ROOT_PARENT, messages_path)
model_path = '../demo/models/smart_home.ent'

code_parser = NodesHandler(model_path, example_message_path)

# validation
validation_node = code_parser.get_node_by_name('Validation')
# c1 = n.rpc_clients[0]
# msg1 = c1.message_module().Request()

# bridges
b1 = code_parser.get_bridge_by_name('RobotR4A2MyRabbit', 'topic')
# b1.run()
