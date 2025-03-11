def one_argument(arg, /):
    return arg.upper()


def three_arguments(a, b, c, /):
    return _format(a, b, c)


def with_normal(posonly, /, normal):
    return _format(posonly, normal)


def with_kwargs(x, /, **y):
    return _format(x, *[f'{k}: {y[k]}' for k in y])


def defaults(required, optional='default', /):
    return _format(required, optional)


def types(first: int, second: float, /):
    return first + second


def _format(*args):
    return ', '.join(args)
