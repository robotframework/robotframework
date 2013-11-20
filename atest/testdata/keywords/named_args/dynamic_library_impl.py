from helper import pretty

# TODO: This file is not really needed. Dynamic libs should do this themselves.

def var_args(*varargs, **kwargs):
    return pretty(*varargs, **kwargs)

def return_argument(arg):
    return arg

def return_arguments(*args):
    return args
