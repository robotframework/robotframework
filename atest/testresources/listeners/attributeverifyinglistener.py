import os
import sys


if sys.version_info[0] > 2:
    long = int
    basestring = str


ROBOT_LISTENER_API_VERSION = '2'

OUTFILE = open(os.path.join(os.getenv('TEMPDIR'), 'listener_attrs.txt'), 'w')
START = 'doc starttime '
END = START + 'endtime elapsedtime status '
SUITE = 'id longname metadata source tests suites totaltests '
TEST = 'id longname tags critical template '
KW = ' kwname libname args assign tags type '
EXPECTED_TYPES = {'elapsedtime': (int, long), 'tags': list, 'args': list,
                  'assign': list, 'metadata': dict, 'tests': list,
                  'suites': list, 'totaltests': int}


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
    names = names.split()
    OUTFILE.write(method_name + '\n')
    if len(names) != len(attrs):
        OUTFILE.write('FAILED: wrong number of attributes\n')
        OUTFILE.write('Expected: %s\nActual: %s\n' % (names, attrs.keys()))
        return
    for name in names:
        value = attrs[name]
        exp_type = EXPECTED_TYPES.get(name, basestring)
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
    raise ValueError(value)


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
