from robot.libraries.BuiltIn import BuiltIn


def get_result_or_error(*args):
    try:
        return BuiltIn().run_keyword(*args)
    except Exception as err:
        return err.message


def pretty(*args, **kwargs):
    args = [to_str(a) for a in args]
    kwargs = [f"{k}:{to_str(v)}" for k, v in sorted(kwargs.items())]
    return ", ".join(args + kwargs)


def to_str(arg):
    if isinstance(arg, str):
        return arg
    return f"{arg} ({type(arg).__name__})"
