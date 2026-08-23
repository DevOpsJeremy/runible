def as_list(value):
    """Ensure a value is returned as a list.

    If ``value`` is already a list it is returned unchanged; otherwise a new
    single-element list containing ``value`` is returned. Useful for accepting
    either scalar or list inputs in configuration parsing.
    """
    if isinstance(value, list):
        return value
    return [value]
