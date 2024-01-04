from eventvalidators import (SeparateMethods, SeparateMethodsAlsoForKeywords,
                             StartEndBobyItemOnly)


class Library:
    ROBOT_LIBRARY_LISTENER = [StartEndBobyItemOnly(),
                              SeparateMethods(),
                              SeparateMethodsAlsoForKeywords()]

    def __init__(self, validate_events=False):
        if not validate_events:
            self.ROBOT_LIBRARY_LISTENER = []
        self.state = 'initial'

    def library_keyword(self, state='initial', number: int = 42, escape=r'c:\temp\new',
                        obj=None):
        if self.state != state:
            raise AssertionError(f"Expected state to be '{state}', "
                                 f"but it was '{self.state}'.")
        if number <= 0 or not isinstance(number, int):
            raise AssertionError(f"Expected number to be a positive integer, "
                                 f"but it was '{number}'.")
        if escape != r'c:\temp\new':
            raise AssertionError(rf"Expected path to be 'c:\temp\new', "
                                 rf"but it was '{escape}'.")
        if obj is not None and obj.attr != number:
            raise AssertionError(f"Expected 'obj.attr' to be {number}, "
                                 f"but it was '{obj.attr}'.")

    def validate_events(self):
        for listener in self.ROBOT_LIBRARY_LISTENER:
            listener.validate()
        if not self.ROBOT_LIBRARY_LISTENER:
            print('Event validation not active.')
