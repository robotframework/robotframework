VARIABLES = dict(exp_return_value=b'ty\xf6paikka',
                 exp_return_msg='ty\\xf6paikka',
                 exp_error_msg="b'hyv\\xe4'",
                 exp_log_msg="b'\\xe4iti'",
                 exp_log_multiline_msg="b'\\xe4iti\\nis\\xe4'")


def get_variables():
    return VARIABLES.copy()
