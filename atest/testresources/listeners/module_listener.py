import os

outpath = os.path.join(os.getenv('TEMPDIR'), 'listen_by_module.txt')
OUTFILE = open(outpath, 'w')
ROBOT_LISTENER_API_VERSION = 2


def start_suite(name, attrs):
    metastr = ' '.join('%s: %s' % (k, v) for k, v in attrs['metadata'].items())
    OUTFILE.write("SUITE START: %s (%s) '%s' [%s]\n"
                  % (name, attrs['id'], attrs['doc'], metastr))

def start_test(name, attrs):
    tags = [str(tag) for tag in attrs['tags']]
    OUTFILE.write("TEST START: %s (%s, line %s) '%s' %s\n"
                  % (name, attrs['id'], attrs['lineno'], attrs['doc'],
                     tags))

def start_keyword(name, attrs):
    if attrs['assign']:
        assign = '%s = ' % ', '.join(attrs['assign'])
    else:
        assign = ''
    name = name + ' ' if name else ''
    if attrs['args']:
        args = '%s ' % [str(a) for a in attrs['args']]
    else:
        args = ''
    OUTFILE.write("%s START: %s%s%s(line %d)\n"
                  % (attrs['type'], assign, name, args, attrs['lineno']))

def log_message(message):
    msg, level = message['message'], message['level']
    if level != 'TRACE' and 'Traceback' not in msg:
        OUTFILE.write('LOG MESSAGE: [%s] %s\n' % (level, msg))

def message(message):
    msg, level = message['message'], message['level']
    if 'Settings' in msg:
        OUTFILE.write('Got settings on level: %s\n' % level)

def end_keyword(name, attrs):
    kw_type = 'KW' if attrs['type'] == 'Keyword' else attrs['type'].upper()
    OUTFILE.write("%s END: %s\n" % (kw_type, attrs['status']))

def end_test(name, attrs):
    if attrs['status'] == 'PASS':
        OUTFILE.write('TEST END: PASS\n')
    else:
        OUTFILE.write("TEST END: %s %s\n"
                      % (attrs['status'], attrs['message']))

def end_suite(name, attrs):
    OUTFILE.write('SUITE END: %s %s\n' % (attrs['status'], attrs['statistics']))

def output_file(path):
    _out_file('Output', path)

def report_file(path):
    _out_file('Report', path)

def log_file(path):
    _out_file('Log', path)

def debug_file(path):
    _out_file('Debug', path)

def _out_file(name, path):
    assert os.path.isabs(path)
    OUTFILE.write('%s: %s\n' % (name, os.path.basename(path)))

def close():
    OUTFILE.write('Closing...\n')
    OUTFILE.close()
