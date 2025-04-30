def kw_only_args(*, kwo):
    pass


def kw_only_args_with_varargs(*varargs, kwo, another="default"):
    pass


def kwargs_and_varargs(*varargs, **kwargs):
    pass


def kwargs_with_everything(a, /, b, c="d", *e, f, g="h", **i):
    pass
