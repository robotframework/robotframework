from helper import pretty


def var_args(*varargs, **kwargs):
    return pretty(*varargs, **kwargs)

def return_argument(arg):
    return arg

def return_arguments(*args):
    return args

def return_kwargs(**kwargs):
    return kwargs
