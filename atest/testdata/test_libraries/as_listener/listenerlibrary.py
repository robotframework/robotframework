import sys

class listenerlibrary(object):

    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.events = []

    def get_events(self):
        return self.events[:]

    def _start_suite(self, name, attrs):
        self.events.append('start suite %s' % name)

    def _start_test(self, name, attrs):
        self.events.append('start test %s' % name)

    def end_test(self, name, attrs):
        self.events.append('end test %s' % name)

    def _start_keyword(self, name, attrs):
        self.events.append('start kw %s' % name)

    def _end_keyword(self, name, attrs):
        self.events.append('end kw %s' % name)

    def _close(self):
        self.events.append('close %s' % self.ROBOT_LIBRARY_SCOPE)
        sys.__stderr__.write("CLOSING %s\n" % self.ROBOT_LIBRARY_SCOPE)

    def events_should_be(self, *expected):
        assert self._format(self.events) == self._format(expected), 'Expected events\n %s\n actual\n %s' % (self._format(expected), self._format(self.events))

    def events_should_be_empty(self):
        assert not self.events, 'Expected empty events, has %s' % self._format(self.events)

    def _format(self, events):
        return ' | '.join(events)

