from robot.libraries.BuiltIn import BuiltIn

def get_result_or_error(*args):
    try:
        return BuiltIn().run_keyword(*args)
    except Exception, err:
        return err.message

def pretty(*args):
    return ', '.join(args)

def lib_mandatory_named_varargs_and_kwargs(a, b='default', *args, **kwargs):
    named = tuple(sorted('%s:%s' % (name, value) for name, value in kwargs.iteritems()))
    return pretty(a, b, *(args+named))

def lib_mandatory_named_and_varargs(a, b='default', *args):
    return pretty(a, b, *args)

def lib_mandatory_and_named(a, b='default'):
    return pretty(a, b)
