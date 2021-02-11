import functools
from textx import metamodel_from_file
import textx.scoping.providers as scoping_providers

from nodem.definitions import GRAMMAR_PATH


def build_model(model_path):
    mm = metamodel_from_file(GRAMMAR_PATH, global_repository=True)
    mm.register_scope_providers(
        {'*.*': scoping_providers.FQNImportURI(importAs=True, )})

    return mm.model_from_file(model_path)


def rgetattr(obj, attr, *args):
    """Enhanced getattr to work in the following case: rgetattr(obj, 'sub1.sub2')"""
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def get_first(iteratable, field, value):
    """Returns the first item in the iterable for which item.field == value"""
    try:
        return next(item for item in iteratable if rgetattr(item, field) == value)
    except StopIteration:
        return


def get_all(iterable, field, value):
    return list(filter(lambda x: rgetattr(x, field) == value, iterable))


def typecasted_value(prop):
    """Typecasting {prop.value} to {prop.type} type

    Args:
        prop (Property Model): Contains "default", "name" and "type" attributes
    """
    type_map = {'float': float, 'int': int, 'bool': bool, 'str': str}
    typecast_func = type_map[prop.type.name]
    if prop.default:
        return typecast_func(prop.default)
