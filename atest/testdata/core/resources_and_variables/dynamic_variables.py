NOT_VARIABLE = True


def get_variables(a, b=None, c=None, d=None):
    if b is None:
        return {'dyn_one_arg': 'Dynamic variable got with one argument',
                'dyn_one_arg_1': 1,
                'LIST__dyn_one_arg_list': ['one', 1],
                'args': [a, b, c, d]}
    if c is None:
        return {'dyn_two_args': 'Dynamic variable got with two arguments',
                'dyn_two_args_False': False,
                'LIST__dyn_two_args_list': ['two', 2],
                'args': [a, b, c, d]}
    if d is None:
        return None
    raise Exception('Ooops!')
