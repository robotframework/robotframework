import sys
from os.path import basename


def get_variables(interpreter=None):
    if sys.version_info[0] < 3 and not _running_on_iron_python(interpreter):
        messages = {'exp_return_msg': 'ty\\xf6paikka',
                    'exp_error_msg': 'hyv\\xe4',
                    'exp_log_msg': '\\xe4ity'}
    else:
        messages = {'exp_return_msg': u'ty\xf6paikka',
                    'exp_error_msg': u'hyv\xe4',
                    'exp_log_msg': u'\xe4ity'}
    return dict(messages, exp_return_value='ty\xf6paikka')


def _running_on_iron_python(interpreter):
    if interpreter:
        return 'ipy' in basename(interpreter)
    return sys.platform == 'cli'
