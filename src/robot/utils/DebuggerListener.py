class DebuggerListener(object):
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self._call_stack = []

    def start_suite(self, name, attributes):
        self._call_stack.append((attributes["source"], name))
        print(self._call_stack[-1])

    def end_suite(self, name, attributes):
        self._call_stack = self._call_stack[:-1]

    def start_test(self, name, attributes):
        self._call_stack.append((attributes["source"], name))
        print(self._call_stack[-1])

    def end_test(self, name, attributes):
        self._call_stack = self._call_stack[:-1]

    def start_keyword(self, name, attributes):
        self._call_stack.append((attributes["source"], attributes["lineno"]))
        print(self._call_stack[-1])

    def end_keyword(self, name, attributes):
        self._call_stack = self._call_stack[:-1]