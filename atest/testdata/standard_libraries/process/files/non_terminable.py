import os.path
import signal
import sys
import time

notify_path = sys.argv[1]


def log(msg, *extra_streams):
    for stream in (sys.stdout,) + extra_streams:
        stream.write(msg + "\n")
        stream.flush()


def ignorer(signum, frame):
    log(f"Ignoring signal {signum}.")


signal.signal(signal.SIGTERM, ignorer)
if hasattr(signal, "SIGBREAK"):
    signal.signal(signal.SIGBREAK, ignorer)

with open(notify_path, "w", encoding="ASCII") as notify:
    log("Starting non-terminable process.", notify)


while True:
    try:
        time.sleep(0.1)
    except IOError:
        pass
    if not os.path.exists(notify_path):
        log("Stopping non-terminable process.")
