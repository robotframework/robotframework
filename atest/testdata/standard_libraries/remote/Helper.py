def get_non_none(*args):
    for arg in args:
        if arg is not None:
            return arg
