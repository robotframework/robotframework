import signal
import time

print 'Starting non-terminable process'

def handler(signum, frame):
    print 'Ignoring signal %d' % signum

signal.signal(signal.SIGTERM, handler)

while True:
    time.sleep(0.1)
