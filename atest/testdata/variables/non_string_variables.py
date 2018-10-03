import sys


def get_variables(interpreter=None):
    variables = {'integer': 42,
                 'float': 3.14,
                 'byte_string': b'hyv\xe4',
                 'byte_string_str': 'hyv\\xe4',
                 'boolean': True,
                 'none': None,
                 'module': sys,
                 'module_str': str(sys),
                 'list': [1, b'\xe4', u'\xe4'],
                 'dict': {b'\xe4': u'\xe4'}}
    variables.update(_get_interpreter_specific_strs(interpreter))
    return variables


def _get_interpreter_specific_strs(interpreter):
    if _python3(interpreter):
        return {'list_str': u"[1, b'\\xe4', '\xe4']",
                'dict_str': u"{b'\\xe4': '\xe4'}"}
    elif _ironpython(interpreter):
        return {'list_str': "[1, b'\\xe4', u'\\xe4']",
                'dict_str': "{b'\\xe4': u'\\xe4'}"}
    else:
        return {'list_str': "[1, '\\xe4', u'\\xe4']",
                'dict_str': "{'\\xe4': u'\\xe4'}"}


def _python3(interpreter=None):
    return interpreter.is_py3 if interpreter else sys.version_info[0] > 2


def _ironpython(interpreter=None):
    return interpreter.is_ironpython if interpreter else sys.platform == 'cli'
