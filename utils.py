def search(iteratable, field, value):
    """Returns the item in the iterable for which item.field == value"""
    try:
        return next(item for item in iteratable if getattr(item, field) == value)
    except StopIteration:
        return


def typecasted_value(property):
    """Typecasting property.value to property.type
    Args:
        property (Property Model): Contains default, name and type attributes
    """
    type_map = {'Float': float, 'Integer': int, 'Boolean': bool}
    typecast_func = type_map[property.type]
    if property.value:
        return typecast_func(property.value)
