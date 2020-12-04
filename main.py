from textx import metamodel_from_file

from parser import NodesHandler

sh_mm = metamodel_from_file('models/grammar.tx')
sh_model = sh_mm.model_from_file('models/sh.ent')

node_handler = NodesHandler(sh_model)
