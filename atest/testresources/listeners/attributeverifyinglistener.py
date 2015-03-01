from six import integer_types, string_types

import os

ROBOT_LISTENER_API_VERSION = '2'

OUTFILE = open(os.path.join(os.getenv('TEMPDIR'), 'listener_attrs.txt'), 'w')
START_ATTRS = 'doc starttime '
END_ATTRS = START_ATTRS + 'endtime elapsedtime status '
EXPECTED_TYPES = {'elapsedtime': integer_types, 'tags': list, 'args': list,
                  'metadata': dict, 'tests': list, 'suites': list,
                  'totaltests': int}


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
    _verify_attrs('START KEYWORD', attrs, START_ATTRS + 'args type')

def end_keyword(name, attrs):
    _verify_attrs('END KEYWORD', attrs, END_ATTRS + 'args type')

def _verify_attrs(method_name, attrs, names):
    names = names.split()
    OUTFILE.write(method_name + '\n')
    if len(names) != len(attrs):
        OUTFILE.write('FAILED: wrong number of attributes\n')
        OUTFILE.write('Expected: %s\nActual: %s\n' % (names, list(attrs.keys())))
        return
    for name in names:
        value = attrs[name]
        exp_type = EXPECTED_TYPES.get(name, string_types)
        if isinstance(value, exp_type):
            OUTFILE.write('PASSED | %s: %s\n' % (name, value))
        else:
            OUTFILE.write('FAILED | %s: %r, Expected: %s, Actual: %s\n'
                          % (name, value, exp_type, type(value)))

def close():
    OUTFILE.close()
