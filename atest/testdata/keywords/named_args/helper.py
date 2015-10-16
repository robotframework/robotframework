from robot.libraries.BuiltIn import BuiltIn
from robot.utils import is_string


def get_result_or_error(*args):
    try:
        return BuiltIn().run_keyword(*args)
    except Exception as err:
        return err.message


def pretty(*args, **kwargs):
    args = [to_str(a) for a in args]
    kwargs = ['%s:%s' % (k, to_str(v)) for k, v in sorted(kwargs.items())]
    return ', '.join(args + kwargs)


def to_str(arg):
    if is_string(arg):
        return arg
    return '%s (%s)' % (arg, type(arg).__name__)
