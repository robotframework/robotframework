import sys

from eventvalidators import (SeparateMethods, SeparateMethodsAlsoForKeywords,
                             StartEndBobyItemOnly)


class Library:
    ROBOT_LIBRARY_LISTENER = [StartEndBobyItemOnly(),
                              SeparateMethods(),
                              SeparateMethodsAlsoForKeywords()]

    def __init__(self, validate_events=True):
        if not validate_events or '--listener' in sys.argv:
            self.ROBOT_LIBRARY_LISTENER = []
        self.state = 'initial'

    def library_keyword(self):
        if self.state != 'initial':
            raise AssertionError(f'state: {self.state}')

    def validate_events(self):
        for listener in self.ROBOT_LIBRARY_LISTENER:
            listener.validate()
        if not self.ROBOT_LIBRARY_LISTENER:
            print('Event validation not active.')
