import sys

ROBOT_LISTENER_API_VERSION = 2


def start_test(name, attrs):
    template = attrs["template"]
    expected = attrs["doc"]
    if template != expected:
        sys.__stderr__.write(f"Expected template '{expected}', got '{template}'.\n")


end_test = start_test
