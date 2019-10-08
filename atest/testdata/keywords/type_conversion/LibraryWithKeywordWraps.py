import functools


def trace(func=None):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


class LibraryWithKeywordWraps:

    @trace
    def keyword_with_wraps(self, arg: int):
        print(arg)
