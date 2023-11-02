import os

OUTFILE = open(os.path.join(os.getenv('TEMPDIR'), 'listener_attrs.txt'), 'w')
START = 'doc starttime '
END = START + 'endtime elapsedtime status '
SUITE = 'id longname metadata source tests suites totaltests '
TEST = 'id longname tags template originalname source lineno '
KW = 'kwname libname args assign tags type lineno source status '
KW_TYPES = {'FOR': 'variables flavor values',
            'WHILE': 'condition limit on_limit on_limit_message',
            'IF': 'condition',
            'ELSE IF': 'condition',
            'EXCEPT': 'patterns pattern_type variable',
            'VAR': 'name value scope',
            'RETURN': 'values'}
FOR_FLAVOR_EXTRA = {'IN ENUMERATE': ' start',
                    'IN ZIP': ' mode fill'}
EXPECTED_TYPES = {'tags': [str],
                  'args': [str],
                  'assign': [str],
                  'metadata': {str: str},
                  'tests': [str],
                  'suites': [str],
                  'totaltests': int,
                  'elapsedtime': int,
                  'lineno': (int, type(None)),
                  'source': (str, type(None)),
                  'variables': (dict, list),
                  'flavor': str,
                  'values': (list, dict),
                  'condition': str,
                  'limit': (str, type(None)),
                  'on_limit': (str, type(None)),
                  'on_limit_message': (str, type(None)),
                  'patterns': (str, list),
                  'pattern_type': (str, type(None)),
                  'variable': (str, type(None)),
                  'value': (str, list)}


def verify_attrs(method_name, attrs, names):
    names = set(names.split())
    OUTFILE.write(method_name + '\n')
    if len(names) != len(attrs):
        OUTFILE.write(f'FAILED: wrong number of attributes\n')
        OUTFILE.write(f'Expected: {sorted(names)}\n')
        OUTFILE.write(f'Actual:   {sorted(attrs)}\n')
        return
    for name in names:
        value = attrs[name]
        exp_type = EXPECTED_TYPES.get(name, str)
        if isinstance(exp_type, list):
            verify_attr(name, value, list)
            for index, item in enumerate(value):
                verify_attr('%s[%s]' % (name, index), item, exp_type[0])
        elif isinstance(exp_type, dict):
            verify_attr(name, value, dict)
            key_type, value_type = dict(exp_type).popitem()
            for key, value in value.items():
                verify_attr('%s[%s] (key)' % (name, key), key, key_type)
                verify_attr('%s[%s] (value)' % (name, key), value, value_type)
        else:
            verify_attr(name, value, exp_type)


def verify_attr(name, value, exp_type):
    if isinstance(value, exp_type):
        OUTFILE.write('passed | %s: %s\n' % (name, format_value(value)))
    else:
        OUTFILE.write('FAILED | %s: %r, Expected: %s, Actual: %s\n'
                      % (name, value, exp_type, type(value)))


def format_value(value):
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return '[%s]' % ', '.join(format_value(item) for item in value)
    if isinstance(value, dict):
        return '{%s}' % ', '.join('%s: %s' % (format_value(k), format_value(v))
                                  for k, v in value.items())
    if value is None:
        return 'None'
    return 'FAILED! Invalid argument type %s.' % type(value)


def verify_name(name, kwname=None, libname=None, **ignored):
    if libname:
        if name != '%s.%s' % (libname, kwname):
            OUTFILE.write("FAILED | KW NAME: '%s' != '%s.%s'\n" % (name, libname, kwname))
    else:
        if name != kwname:
            OUTFILE.write("FAILED | KW NAME: '%s' != '%s'\n" % (name, kwname))
        if libname != '':
            OUTFILE.write("FAILED | LIB NAME: '%s' != ''\n" % libname)


class VerifyAttributes:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self):
        self._keyword_stack = []

    def start_suite(self, name, attrs):
        verify_attrs('START SUITE', attrs, START + SUITE)

    def end_suite(self, name, attrs):
        verify_attrs('END SUITE', attrs, END + SUITE + 'statistics message')

    def start_test(self, name, attrs):
        verify_attrs('START TEST', attrs, START + TEST)

    def end_test(self, name, attrs):
        verify_attrs('END TEST', attrs, END + TEST + 'message')

    def start_keyword(self, name, attrs):
        type_ = attrs['type']
        extra = KW_TYPES.get(type_, '')
        if type_ == 'ITERATION' and self._keyword_stack[-1] == 'FOR':
            extra += ' variables'
        if type_ == 'FOR':
            extra += FOR_FLAVOR_EXTRA.get(attrs['flavor'], '')
        verify_attrs('START ' + type_, attrs, START + KW + extra)
        if type_ in ('KEYWORD', 'SETUP', 'TEARDOWN'):
            verify_name(name, **attrs)
        self._keyword_stack.append(type_)

    def end_keyword(self, name, attrs):
        self._keyword_stack.pop()
        type_ = attrs['type']
        extra = KW_TYPES.get(type_, '')
        if type_ == 'ITERATION' and self._keyword_stack[-1] == 'FOR':
            extra += ' variables'
        if type_ == 'FOR':
            extra += FOR_FLAVOR_EXTRA.get(attrs['flavor'], '')
        verify_attrs('END ' + type_, attrs, END + KW + extra)
        if type_ in ('KEYWORD', 'SETUP', 'TEARDOWN'):
            verify_name(name, **attrs)

    def close(self):
        OUTFILE.close()
