import sys

class listenerlibrary3(object):
    ROBOT_LISTENER_API_VERSION = 3
    ROBOT_LIBRARY_SCOPE = "TEST CASE"

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self

    def start_suite(self, data, result):
        result.doc = (result.doc + ' [start suite]').strip()
        result.metadata['suite'] = '[start]'
        result.metadata['tests'] = ''
        assert len(data.tests) == 2
        assert len(result.tests) == 0
        data.tests.create(name='New')

    def end_suite(self, data, result):
        assert len(data.tests) == 3
        assert len(result.tests) == 3
        assert result.doc.endswith('[start suite]')
        assert result.metadata['suite'] == '[start]'
        result.name += ' [end suite]'
        result.doc += ' [end suite]'
        result.metadata['suite'] += ' [end]'

    def start_test(self, data, result):
        result.doc = (result.doc + ' [start test]').strip()
        result.tags.add('[start]')
        result.message = 'Message: [start]'
        result.parent.metadata['tests'] += 'x'
        data.body.create_keyword('No Operation')

    def end_test(self, data, result):
        result.doc += ' [end test]'
        result.tags.add('[end]')
        result.passed = not result.passed
        result.message += ' [end]'

    def log_message(self, msg):
        msg.message += ' [log_message]'
        msg.timestamp = '20151216 15:51:20.141'

    def foo(self):
        print("*WARN* Foo")

    def message(self, msg):
        msg.message += ' [message]'
        msg.timestamp = '20151216 15:51:20.141'

    def close(self):
        sys.__stderr__.write('CLOSING Listener library 3\n')
