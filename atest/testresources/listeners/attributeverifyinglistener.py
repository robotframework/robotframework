import os
import sys


if sys.version_info[0] > 2:
    long = int
    basestring = str


ROBOT_LISTENER_API_VERSION = '2'

OUTFILE = open(os.path.join(os.getenv('TEMPDIR'), 'listener_attrs.txt'), 'w')
START_ATTRS = 'doc starttime '
END_ATTRS = START_ATTRS + 'endtime elapsedtime status '
KW_ATTRS = 'args assign kwname libname type'
EXPECTED_TYPES = {'elapsedtime': (int, long), 'tags': list, 'args': list,
                  'assign': list, 'metadata': dict, 'tests': list,
                  'suites': list, 'totaltests': int}


def start_suite(name, attrs):
    _verify_attrs('START SUITE', attrs,
                  START_ATTRS + 'id longname metadata source tests suites totaltests')

def end_suite(name, attrs):
    _verify_attrs('END SUITE', attrs,
                  END_ATTRS + 'id longname metadata source tests suites totaltests statistics message')

def start_test(name, attrs):
    _verify_attrs('START TEST', attrs,
                  START_ATTRS + 'id longname tags critical template')

def end_test(name, attrs):
    _verify_attrs('END TEST', attrs,
                  END_ATTRS + 'id longname tags critical message template')

def start_keyword(name, attrs):
    _verify_attrs('START KEYWORD', attrs, START_ATTRS + KW_ATTRS)
    _verify_name(name, **attrs)

def end_keyword(name, attrs):
    _verify_attrs('END KEYWORD', attrs, END_ATTRS + KW_ATTRS)
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
            OUTFILE.write('PASSED | %s: %s\n' % (name, value))
        else:
            OUTFILE.write('FAILED | %s: %r, Expected: %s, Actual: %s\n'
                          % (name, value, exp_type, type(value)))

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
