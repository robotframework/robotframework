from sys import stdout, stderr
from time import sleep

stdout.write('start stdout\n')
stdout.flush()
stderr.write('start stderr\n')
stderr.flush()
sleep(1)
stdout.write('end stdout\n')
stdout.flush()
stderr.write('end stderr\n')
stderr.flush()
