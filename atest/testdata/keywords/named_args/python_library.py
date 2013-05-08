from helper import pretty

def lib_mandatory_named_varargs_and_kwargs(a, b='default', *args, **kwargs):
    return pretty(a, b, *args, **kwargs)

def lib_kwargs(**kwargs):
    return pretty(**kwargs)

def lib_mandatory_named_and_kwargs(a, b=2, **kwargs):
    return pretty(a, b, **kwargs)

def lib_mandatory_named_and_varargs(a, b='default', *args):
    return pretty(a, b, *args)

def lib_mandatory_and_named(a, b='default'):
    return pretty(a, b)

def lib_mandatory_and_named_2(a, b='default', c='default'):
    return pretty(a, b, c)
