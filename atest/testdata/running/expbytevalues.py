import sys

from robot.utils import console_decode


VARIABLES = dict(exp_return_value=b'ty\xf6paikka',
                 exp_return_msg='ty\\xf6paikka',
                 exp_error_msg='hyv\\xe4',
                 exp_log_msg='\\xe4iti',
                 exp_log_multiline_msg='\\xe4iti\nis\\xe4')


def get_variables(interpreter=None):
    variables = VARIABLES.copy()
    if _running_on_iron_python(interpreter):
        variables.update(exp_return_msg=b'ty\xf6paikka',
                         exp_error_msg=u'hyv\xe4',
                         exp_log_msg=u'\xe4iti',
                         exp_log_multiline_msg=u'\xe4iti\nis\xe4')
    elif _running_on_py3(interpreter):
        variables.update(exp_error_msg="b'hyv\\xe4'",
                         exp_log_msg="b'\\xe4iti'",
                         exp_log_multiline_msg="b'\\xe4iti\\nis\\xe4'")
    elif _high_bytes_ok():
        variables.update(exp_log_msg=console_decode(b'\xe4iti'),
                         exp_log_multiline_msg=console_decode(b'\xe4iti\nis\xe4'))
    return variables


def _running_on_iron_python(interpreter=None):
    if interpreter:
        return interpreter.is_ironpython
    return sys.platform == 'cli'

def _running_on_py3(interpreter=None):
    if interpreter:
        return interpreter.is_py3
    return sys.version_info[0] == 3

def _high_bytes_ok():
    return console_decode('\xe4') != '\\xe4'
