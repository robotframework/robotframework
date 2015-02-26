no_args_vars = {
    'dyn_no_args_get_var': 'Dyn var got with no args from get_variables',
    'dyn_no_args_get_var_2': 2,
    'LIST__dyn_no_args_get_var_list': ['one', 2]
}
one_arg_vars = {
    'dyn_one_arg_get_var': 'Dyn var got with one arg from get_variables',
    'dyn_one_arg_get_var_False': False,
    'LIST__dyn_one_arg_get_var_list': ['one', False, no_args_vars]
}


def get_variables(*args):
    if len(args) == 0:
        return no_args_vars
    if len(args) == 1:
        return one_arg_vars
    if len(args) == 2:
        return None   # this is invalid
    raise Exception('Invalid arguments for get_variables')
