import os
import tempfile
    
outpath = os.path.join(tempfile.gettempdir(), 'listen_by_module.txt')
OUTFILE = open(outpath, 'w')
ROBOT_LISTENER_API_VERSION = 2

    
def start_suite(name, attrs):
    OUTFILE.write("SUITE START: %s '%s'\n" % (name, attrs['doc']))
    
def start_test(name, attrs):
    tags = [ str(tag) for tag in attrs['tags'] ]
    OUTFILE.write("TEST START: %s '%s' %s\n" % (name, attrs['doc'], tags))

def start_keyword(name, attrs):
    args = [ str(arg) for arg in attrs['args'] ]
    OUTFILE.write("KW START: %s %s\n" % (name, args))

def log_message(message, level):
    if level != 'TRACE' and 'Traceback' not in message:
        OUTFILE.write('LOG MESSAGE: [%s] %s\n' % (level, message))

def end_keyword(name, attrs):
    OUTFILE.write("KW END: %s\n" % (attrs['status']))        

def end_test(name, attrs):
    if attrs['status'] == 'PASS':
        OUTFILE.write('TEST END: PASS\n')
    else:
        OUTFILE.write("TEST END: %s %s\n" % (attrs['status'], attrs['message']))        
        
def end_suite(name, attrs):
    OUTFILE.write('SUITE END: %s %s\n' % (attrs['status'], attrs['statistics']))

def output_file(path):
    _out_file('Output', path)
        
def summary_file(path):
    _out_file('Summary', path)
                
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
