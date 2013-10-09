import signal

signal.signal(signal.SIGTERM, lambda *x: None)

while(True):
	pass
