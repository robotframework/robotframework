import os
import tempfile


ROBOT_LISTENER_API_VERSION = '2'
OUTFILE = open(os.path.join(tempfile.gettempdir(), 'listener_attrs.txt'), 'w')

START_ATTRIBUTES = ['doc', 'starttime']
END_ATTRIBUTES = START_ATTRIBUTES + ['endtime', 'elapsedtime', 'status']
EXPECTED_TYPES = {'elapsedtime': long, 'tags': list, 'args': list}


def start_suite(name, attrs):
    _verify_attributes('START SUITE', attrs, START_ATTRIBUTES+['longname'])

def end_suite(name, attrs):
    _verify_attributes('END SUITE', attrs, END_ATTRIBUTES+['longname', 'statistics', 'message'])

def start_test(name, attrs):
    _verify_attributes('START TEST', attrs, START_ATTRIBUTES + ['longname', 'tags'])

def end_test(name, attrs):
    _verify_attributes('END TEST', attrs, END_ATTRIBUTES + ['longname', 'tags', 'message'])

def start_keyword(name, attrs):
    _verify_attributes('START KEYWORD', attrs, START_ATTRIBUTES + ['args'])

def end_keyword(name, attrs):
    _verify_attributes('END KEYWORD', attrs, END_ATTRIBUTES + ['args'])

def _verify_attributes(method_name, attrs, names):
    OUTFILE.write(method_name + '\n')
    if len(names) != len(attrs):
        OUTFILE.write('FAILED: wrong number of attributes\n')
        OUTFILE.write('Expected: %s\nActual: %s\n' % (names, attrs.keys()))
        return
    for name in names:
        status = isinstance(attrs[name], EXPECTED_TYPES.get(name, basestring))\
                and 'PASSED' or 'FAILED'
        OUTFILE.write('%s | %s: %s\n' %(status, name, attrs[name]))

def close():
    OUTFILE.close()

