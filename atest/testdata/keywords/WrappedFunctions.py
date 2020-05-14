from functools import wraps


def decorator(f):
    @wraps(f)
    def wrapper(*args, **kws):
        return f(*args, **kws)
    return wrapper


@decorator
def wrapped_function():
    pass


@decorator
def wrapped_function_with_arguments(a, b=2):
    pass
