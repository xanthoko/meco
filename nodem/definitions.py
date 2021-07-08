from os.path import dirname

ROOT_PATH = dirname(__file__)
ROOT_PARENT = dirname(ROOT_PATH)
MODELS_DIR_PATH = ROOT_PATH + '/models'
GRAMMAR_PATH = MODELS_DIR_PATH + '/grammar.tx'
MESSAGES_MODEL_PATH = MODELS_DIR_PATH + '/messages.idl'
MESSAGES_DIR_PATH = ROOT_PATH + '/msgs'
TEMPLATES_DIR_PATH = ROOT_PATH + '/templates'
PLANTUML_MODELS_DIR_PATH = ROOT_PATH + '/plantuml_models'
OUTPUTS_DIR_PATH = ROOT_PATH + '/outputs'
CODE_OUTPUTS_DIR_PATH = ROOT_PATH + '/code_outputs'
