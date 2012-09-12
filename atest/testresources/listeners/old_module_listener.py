import os

outpath = os.path.join(os.getenv('TEMPDIR'), 'listen_by_module.txt')
OUTFILE = open(outpath, 'w')


def start_suite(name, doc):
    OUTFILE.write("SUITE START: %s '%s'\n" % (name, doc))

def start_test(name, doc, tags):
    tags = [ str(tag) for tag in tags ]
    OUTFILE.write("TEST START: %s '%s' %s\n" % (name, doc, tags))

def start_keyword(name, args):
    args = [str(arg) for arg in args]
    OUTFILE.write("KW START: %s %s\n" % (name, args))

def end_keyword(status):
    OUTFILE.write("KW END: %s\n" % (status))

def end_test(status, message):
    if status == 'PASS':
        OUTFILE.write('TEST END: PASS\n')
    else:
        OUTFILE.write("TEST END: %s %s\n" % (status, message))

def end_suite(status, message):
    OUTFILE.write('SUITE END: %s %s\n' % (status, message))

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
