from helper import pretty


def var_args(*varargs):
    return pretty(*varargs)

def mandatory_named_and_varargs(a, b='default', *varargs):
    return pretty(a, b, *varargs)

def mandatory_and_named(a, b='default'):
    return pretty(a, b)

def one_kwarg(kwarg=''):
    return kwarg

def two_kwargs(first='', second=''):
    return pretty(first, second)

def four_kw_args(a='default', b='default', c='default', d='default'):
    return pretty(a, b, c, d)

def mandatory_and_kwargs(man1, man2, kwarg='KWARG VALUE'):
    return pretty(man1, man2, kwarg)

def escaped_default_value(d1='${notvariable}', d2='\\\\', d3='\n', d4='\t'):
    return '%s %s %s %s' % (d1, d2, d3, d4)

def named_arguments_with_varargs(a='default', b='default', *varargs):
    return a, b, varargs


