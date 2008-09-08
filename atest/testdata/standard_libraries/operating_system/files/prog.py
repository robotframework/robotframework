import sys


def output(stdout=None, stderr=None, count=1):
    if stdout is not None:
        sys.stdout.write((stdout+'\n') * int(count))
    if stderr is not None:
        sys.stderr.write((stderr+'\n') * int(count))
    

if __name__ == '__main__':
    args = sys.argv[1:]
    try:
        rc = int(args[0])
        args = args[1:]
    except (IndexError, ValueError):
        rc = 0
    output(*args)
    sys.exit(rc)
