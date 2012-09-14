import sys
from os.path import basename


def get_variables(interpreter=None):
    return {'integer': 42,
            'float': 3.14,
            'byte_string': 'hyv\xe4',
            'byte_string_str': _byte_string_str(interpreter),
            'boolean': True,
            'none': None,
            'module': sys,
            'module_str': str(sys),
            'list': [1, '\xe4', u'\xe4'],
            'list_str': "[1, '\\xe4', u'\\xe4']",
            'dict': {'\xe4': u'\xe4'},
            'dict_str': "{'\\xe4': u'\\xe4'}"}

def _byte_string_str(interpreter):
    return 'hyv\\xe4' if not _running_on_iron_python(interpreter) else 'hyv\xe4'

def _running_on_iron_python(interpreter):
    if interpreter:
        return 'ipy' in basename(interpreter)
    return sys.platform == 'cli'
