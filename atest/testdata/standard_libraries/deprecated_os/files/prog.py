import sys


def run(rc=0, stdout=None, stderr=None):
    output(stdout, sys.stdout)
    output(stderr, sys.stderr)
    return int(rc)
    
    
def output(msg, stream=sys.stdout):
    if msg is not None:
        stream.write(msg + '\n')
    

if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        rc = run(*args)
    except Exception, err:
        output("Running failed with args %s for exception: %s" % (args, err))
        rc = 255
    sys.exit(rc)
