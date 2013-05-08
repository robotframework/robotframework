from robot.libraries.BuiltIn import BuiltIn

def get_result_or_error(*args):
    try:
        return BuiltIn().run_keyword(*args)
    except Exception, err:
        return err.message

def pretty(*args, **kwargs):
    args = [to_str(a) for a in args]
    kwargs = sorted('%s:%s' % (n, to_str(v)) for n, v in kwargs.items())
    return ', '.join(args + kwargs)

def to_str(arg):
    if isinstance(arg, basestring):
        return arg
    return '%s (%s)' % (arg, type(arg).__name__)
