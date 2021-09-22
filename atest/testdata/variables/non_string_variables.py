import sys


def get_variables():
    variables = {'integer': 42,
                 'float': 3.14,
                 'byte_string': b'hyv\xe4',
                 'byte_string_str': 'hyv\\xe4',
                 'boolean': True,
                 'none': None,
                 'module': sys,
                 'module_str': str(sys),
                 'list': [1, b'\xe4', '\xe4'],
                 'dict': {b'\xe4': '\xe4'},
                 'list_str': u"[1, b'\\xe4', '\xe4']",
                 'dict_str': u"{b'\\xe4': '\xe4'}"}
    return variables

