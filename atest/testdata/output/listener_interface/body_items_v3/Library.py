from eventvalidators import (SeparateMethods, SeparateMethodsAlsoForKeywords,
                             StartEndBobyItemOnly)


class Library:
    ROBOT_LIBRARY_LISTENER = [
        StartEndBobyItemOnly(),
        SeparateMethods(),
        SeparateMethodsAlsoForKeywords()
    ]

    def library_keyword(self):
        pass

    def validate_events(self):
        for listener in self.ROBOT_LIBRARY_LISTENER:
            listener.validate()
        print('All methods called correctly.')
