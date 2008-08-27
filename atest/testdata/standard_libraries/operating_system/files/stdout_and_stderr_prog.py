import sys


def run(stdout=None, stderr=None):
    output(stdout, sys.stdout)
    output(stderr, sys.stderr)
    
def output(msg, stream=sys.stdout):
    if msg is not None:
        stream.write(msg)
    

if __name__ == '__main__':
    run(*sys.argv[1:])

