from functools import wraps


def decorator(f):
    @wraps(f)
    def wrapper(*args, **kws):
        return f(*args, **kws)
    return wrapper


class WrappedMethods:

    @decorator
    def wrapped_method(self):
        pass

    @decorator
    def wrapped_method_with_arguments(self, a, b=2):
        pass
