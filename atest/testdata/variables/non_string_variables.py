import sys
from os.path import basename


def get_variables(interpreter=None):
    variables = {'integer': 42,
                 'float': 3.14,
                 'byte_string': 'hyv\xe4',
                 'boolean': True,
                 'none': None,
                 'module': sys,
                 'module_str': str(sys),
                 'list': [1, '\xe4', u'\xe4'],
                 'dict': {'\xe4': u'\xe4'}}
    variables.update(_get_interpreter_specific_strs(interpreter))
    return variables

def _get_interpreter_specific_strs(interpreter):
    if not _running_on_iron_python(interpreter):
        return {'byte_string_str': 'hyv\\xe4',
                'list_str': "[1, '\\xe4', u'\\xe4']",
                'dict_str': "{'\\xe4': u'\\xe4'}"}
    else:
        return {'byte_string_str': u'hyv\xe4',
                'list_str': "[1, u'\\xe4', u'\\xe4']",
                'dict_str': "{u'\\xe4': u'\\xe4'}"}

def _running_on_iron_python(interpreter):
    if interpreter:
        return 'ipy' in basename(interpreter)
    return sys.platform == 'cli'
