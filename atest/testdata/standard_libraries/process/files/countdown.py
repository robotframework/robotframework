from __future__ import with_statement
import sys
import time

path = sys.argv[1]
with open(path, 'w') as f:
    for i in range(10, 0, -1):
        f.write('%d\n' % i)
        f.flush()
        time.sleep(0.1)
    f.write('BLASTOFF')
