def search(iteratable, field, value):
    """Finds the item in the iterable that has item.fiedl == value"""
    try:
        return next(item for item in iteratable if getattr(item, field) == value)
    except StopIteration:
        return
