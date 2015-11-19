from listenerlibrary import listenerlibrary


class multiple_listenerlibrary(object):

    def __init__(self, fail=False):
        self.instances = [
            listenerlibrary(),
            listenerlibrary(),
        ]
        if fail:
            class V1Listener(object):
                def events_should_be_empty(self):
                    return True
            self.instances.append(V1Listener())
        self.ROBOT_LIBRARY_LISTENER = self.instances

    def events_should_be(self, *expected):
        for inst in self.instances:
            inst.events_should_be(*expected)

    def events_should_be_empty(self):
        for inst in self.instances:
            inst.events_should_be_empty()
