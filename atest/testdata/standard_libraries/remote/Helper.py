def evaluate_if_string(thing):
    return eval(thing) if isinstance(thing, basestring) else thing

def get_non_none(*args):
    for arg in args:
        if arg is not None:
            return arg
