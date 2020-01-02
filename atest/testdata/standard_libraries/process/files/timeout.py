from sys import argv, stdout, stderr
from time import sleep

timeout = float(argv[1]) if len(argv) > 1 else 1

stdout.write('start stdout\n')
stdout.flush()
stderr.write('start stderr\n')
stderr.flush()
sleep(timeout)
stdout.write('end stdout\n')
stdout.flush()
stderr.write('end stderr\n')
stderr.flush()
