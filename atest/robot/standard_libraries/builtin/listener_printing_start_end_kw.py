import sys

ROBOT_LISTENER_API_VERSION = 2


def start_keyword(name, attrs):
    sys.stdout.write(f"start keyword {name}\n")
    sys.stderr.write(f"start keyword {name}\n")


def end_keyword(name, attrs):
    sys.stdout.write(f"end keyword {name}\n")
    sys.stderr.write(f"end keyword {name}\n")
