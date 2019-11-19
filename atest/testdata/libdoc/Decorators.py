from functools import wraps


__all__ = ['keyword_using_decorator', 'keyword_using_decorator_with_wraps']


def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def decorator_with_wraps(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@decorator
def keyword_using_decorator(args, are_not, preserved=True):
    return '%s %s %s' % (args, are_not, preserved)


@decorator_with_wraps
def keyword_using_decorator_with_wraps(args, are, preserved=True):
    pass
