from robot.api import SuiteVisitor


ROBOT_LISTENER_API_VERSION = 3


def start_suite(data, result):
    result.name += ' [start suite]'
    result.doc += ' [start suite]'
    result.metadata['Suite'] = '[start]'
    data.name = data.doc = 'Not visible in results'
    assert len(data.tests) == 2
    data.tests.create(name='New')
    data.visit(TestModifier())


def end_suite(data, result):
    assert len(data.tests) == 3
    assert data.name == data.doc == 'Not visible in results'
    assert result.name.endswith('[start suite]')
    assert result.doc.endswith('[start suite]')
    assert result.metadata['suite'] == '[start]'
    result.name += ' [end suite]'
    result.doc += ' [end suite]'
    result.metadata['suite'] += ' [end]'
    for test in result.tests:
        test.name = 'Not visible in reports'
        test.status = 'PASS'    # Not visible in reports


def startTest(data, result):
    result.name += ' [start test]'
    result.doc += ' [start test]'
    result.tags.add('[start]')
    result.message = 'Message: [start]'
    data.name = data.doc = 'Not visible in results'
    data.keywords.create('No Operation')


def end_test(data, result):
    result.name = 'Does not go to output.xml'
    result.doc += ' [end test]'
    result.tags.add('[end]')
    result.passed = not result.passed
    result.message += ' [end]'
    data.name = data.doc = 'Not visible in results'


def log_message(msg):
    msg.message = msg.message.upper()
    msg.timestamp = '20151216 15:51:20.141'


message = log_message


def start_keyword(*args):
    raise SystemExit('Should not be called!')


def end_keyword(*args):
    raise SystemExit('Should not be called!')


class TestModifier(SuiteVisitor):

    def visit_test(self, test):
        test.name += ' [start suite]'
        test.doc += ' [start suite]'
        test.tags.add('[start suite]')
