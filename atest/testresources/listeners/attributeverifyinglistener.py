import os

try:
    basestring
    long
except NameError:
    basestring = str
    long = int


ROBOT_LISTENER_API_VERSION = '2'

OUTFILE = open(os.path.join(os.getenv('TEMPDIR'), 'listener_attrs.txt'), 'w')
START = 'doc starttime '
END = START + 'endtime elapsedtime status '
SUITE = 'id longname metadata source tests suites totaltests '
TEST = 'id longname tags template originalname source lineno '
KW = 'kwname libname args assign tags type lineno source status '
EXPECTED_TYPES = {'tags': [basestring], 'args': [basestring],
                  'assign': [basestring], 'metadata': {basestring: basestring},
                  'tests': [basestring], 'suites': [basestring],
                  'totaltests': int, 'elapsedtime': (int, long),
                  'lineno': (int, type(None)), 'source': (basestring, type(None))}


def start_suite(name, attrs):
    _verify_attrs('START SUITE', attrs, START + SUITE)


def end_suite(name, attrs):
    _verify_attrs('END SUITE', attrs, END + SUITE + 'statistics message')


def start_test(name, attrs):
    _verify_attrs('START TEST', attrs, START + TEST)


def end_test(name, attrs):
    _verify_attrs('END TEST', attrs, END + TEST + 'message')


def start_keyword(name, attrs):
    _verify_attrs('START KEYWORD', attrs, START + KW)
    _verify_name(name, **attrs)


def end_keyword(name, attrs):
    _verify_attrs('END KEYWORD', attrs, END + KW)
    _verify_name(name, **attrs)


def _verify_attrs(method_name, attrs, names):
    names = set(names.split())
    OUTFILE.write(method_name + '\n')
    if len(names) != len(attrs):
        OUTFILE.write('FAILED: wrong number of attributes\n')
        OUTFILE.write('Expected: %s\nActual: %s\n' % (names, attrs.keys()))
        return
    for name in names:
        value = attrs[name]
        exp_type = EXPECTED_TYPES.get(name, basestring)
        if isinstance(exp_type, list):
            _verify_attr(name, value, list)
            for index, item in enumerate(value):
                _verify_attr('%s[%s]' % (name, index), item, exp_type[0])
        elif isinstance(exp_type, dict):
            _verify_attr(name, value, dict)
            key_type, value_type = dict(exp_type).popitem()
            for key, value in value.items():
                _verify_attr('%s[%s] (key)' % (name, key), key, key_type)
                _verify_attr('%s[%s] (value)' % (name, key), value, value_type)
        else:
            _verify_attr(name, value, exp_type)


def _verify_attr(name, value, exp_type):
    if isinstance(value, exp_type):
        OUTFILE.write('PASSED | %s: %s\n' % (name, _format(value)))
    else:
        OUTFILE.write('FAILED | %s: %r, Expected: %s, Actual: %s\n'
                      % (name, value, exp_type, type(value)))


def _format(value):
    if isinstance(value, basestring):
        return value
    if isinstance(value, (int, long)):
        return str(value)
    if isinstance(value, list):
        return '[%s]' % ', '.join(_format(item) for item in value)
    if isinstance(value, dict):
        return '{%s}' % ', '.join('%s: %s' % (_format(k), _format(v))
                                  for k, v in value.items())
    if value is None:
        return 'None'
    return 'FAILED! Invalid argument type %s.' % type(value)


def _verify_name(name, kwname=None, libname=None, **ignored):
    if libname:
        if name != '%s.%s' % (libname, kwname):
            OUTFILE.write("FAILED | KW NAME: '%s' != '%s.%s'\n" % (name, libname, kwname))
    else:
        if name != kwname:
            OUTFILE.write("FAILED | KW NAME: '%s' != '%s'\n" % (name, kwname))
        if libname != '':
            OUTFILE.write("FAILED | LIB NAME: '%s' != ''\n" % libname)


def close():
    OUTFILE.close()
