import functools


def rgetattr(obj, attr, *args):
    """Enhanced getattr to work in this case: rgetattr(obj, 'sub1.sub2')"""
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split('.'))


def search(iteratable, field, value):
    """Returns the item in the iterable for which item.field == value"""
    try:
        return next(item for item in iteratable if rgetattr(item, field) == value)
    except StopIteration:
        return


def get_all(iterable, field, value):
    return list(filter(lambda x: rgetattr(x, field) == value, iterable))


def typecasted_value(property):
    """Typecasting property.value to property.type

    Args:
        property (Property Model): Contains default, name and type attributes
    """
    type_map = {'Float': float, 'Integer': int, 'Boolean': bool}
    typecast_func = type_map[property.type]
    if property.value:
        return typecast_func(property.value)
