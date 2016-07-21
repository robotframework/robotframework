from listenerlibrary import listenerlibrary


class multiple_listenerlibrary(object):

    def __init__(self, fail=False):
        self.instances = [
            listenerlibrary(),
            listenerlibrary(),
        ]
        if fail:
            class NoVersionListener(object):
                def events_should_be_empty(self):
                    pass
            self.instances.append(NoVersionListener())
        self.ROBOT_LIBRARY_LISTENER = self.instances

    def events_should_be(self, *expected):
        for inst in self.instances:
            inst.events_should_be(*expected)

    def events_should_be_empty(self):
        for inst in self.instances:
            inst.events_should_be_empty()
