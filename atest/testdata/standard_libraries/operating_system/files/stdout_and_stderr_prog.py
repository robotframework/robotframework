import sys


def run(stdout=None, stderr=None):
    output(stdout, sys.stdout)
    output(stderr, sys.stderr)
    
def output(msg, stream):
    if msg is not None:
        stream.write(msg)
    

if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        run(*args)
    except Exception, err:
        output("Running failed with args %s for exception: %s" % (args, err))
