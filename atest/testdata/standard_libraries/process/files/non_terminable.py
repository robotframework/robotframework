import signal
import time
import sys
import os.path


notify_path = sys.argv[1]

def log(msg, *extra_streams):
    for stream in (sys.stdout,) + extra_streams:
        stream.write(msg + '\n')
        stream.flush()

def ignorer(signum, frame):
    log('Ignoring signal %d.' % signum)

signal.signal(signal.SIGTERM, ignorer)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, ignorer)

with open(notify_path, 'w') as notify:
    log('Starting non-terminable process.', notify)


while True:
    try:
        time.sleep(0.1)
    except IOError:
        pass
    if not os.path.exists(notify_path):
        log('Stopping non-terminable process.')
