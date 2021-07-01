import os

from nodem.parser import EntitiesHandler
from nodem.definitions import ROOT_PARENT

messages_path = 'demo/models/sh_messages.idl'
example_message_path = os.path.join(ROOT_PARENT, messages_path)
model_path = '../demo/models/smart_home.ent'

# --- Code generation ---
code_parser = EntitiesHandler(model_path, example_message_path)
# publishers
# p1 = code_parser.get_publisher_by_topic('kitchen.temperature')
# p2 = code_parser.get_publisher_by_topic('bedroom.temperature')
# p3 = code_parser.get_publisher_by_topic('bathroom.humidity')
# p4 = code_parser.get_publisher_by_topic('kitchen.intruder_detected')
# p5 = code_parser.get_publisher_by_topic('robot.pose')
# # services
# s1 = code_parser.get_node_by_name('RelayService').rpc_services[0]
