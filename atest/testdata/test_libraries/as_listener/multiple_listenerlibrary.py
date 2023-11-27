from listenerlibrary import listenerlibrary


class multiple_listenerlibrary:

    def __init__(self, fail=False):
        self.instances = [
            listenerlibrary(),
            listenerlibrary(),
        ]
        if fail:
            class BadVersionListener:
                ROBOT_LISTENER_API_VERSION = 666
                def events_should_be_empty(self):
                    pass
            self.instances.append(BadVersionListener())
        self.ROBOT_LIBRARY_LISTENER = self.instances

    def events_should_be(self, *expected):
        for inst in self.instances:
            inst.events_should_be(*expected)

    def events_should_be_empty(self):
        for inst in self.instances:
            inst.events_should_be_empty()
