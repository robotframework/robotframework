import sys


def output(rc=0, stdout='', stderr='', count=1):
    if stdout:
        sys.stdout.write((stdout+'\n') * int(count))
    if stderr:
        sys.stderr.write((stderr+'\n') * int(count))
    return int(rc)


if __name__ == '__main__':
    rc = output(*sys.argv[1:])
    sys.exit(rc)
