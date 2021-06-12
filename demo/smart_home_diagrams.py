import os

from nodem.definitions import ROOT_PARENT
from nodem.diagram_parser import DiagramHandler

messages_path = 'demo/models/sh_messages.idl'
example_message_path = os.path.join(ROOT_PARENT, messages_path)
model_path = '../demo/models/smart_home.ent'

# --- Documentation diagrams generation ---
dh = DiagramHandler(model_path)
dh.create_documentation()
