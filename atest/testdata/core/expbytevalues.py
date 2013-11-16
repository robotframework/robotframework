import sys
from os.path import basename

from robot.utils import decode_output


VARIABLES = dict(exp_return_value='ty\xf6paikka',
                 exp_return_msg='ty\\xf6paikka',
                 exp_error_msg='hyv\\xe4',
                 exp_log_msg='\\xe4iti',
                 exp_log_multiline_msg='\\xe4iti\nis\\xe4')


def get_variables(interpreter=None):
    variables = VARIABLES.copy()
    if _running_on_iron_python(interpreter):
        variables.update(exp_return_msg=u'ty\xf6paikka',
                         exp_error_msg=u'hyv\xe4',
                         exp_log_msg=u'\xe4iti',
                         exp_log_multiline_msg=u'\xe4iti\nis\xe4')
    elif _high_bytes_ok():
        variables.update(exp_log_msg=decode_output('\xe4iti'),
                         exp_log_multiline_msg=decode_output('\xe4iti\nis\xe4'))
    return variables


def _running_on_iron_python(interpreter):
    if interpreter:
        return 'ipy' in basename(interpreter)
    return sys.platform == 'cli'


def _high_bytes_ok():
    return decode_output('\xe4') != '\\xe4'
