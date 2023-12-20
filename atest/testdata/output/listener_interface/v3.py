import sys

from robot.api import SuiteVisitor


ROBOT_LISTENER_API_VERSION = 3


def start_suite(data, result):
    data.name = data.doc = result.name = 'Not visible in results'
    result.doc = (result.doc + ' [start suite]').strip()
    result.metadata['suite'] = '[start]'
    result.metadata['tests'] = ''
    result.metadata['number'] = 42
    assert len(data.tests) == 2
    assert len(result.tests) == 0
    data.tests.create(name='Added by start_suite')
    data.visit(TestModifier())


def end_suite(data, result):
    assert len(data.tests) == 5, '%d tests, not 5' % len(data.tests)
    assert len(result.tests) == 5, '%d tests, not 5' % len(result.tests)
    for test in result.tests:
        if test.setup or test.body or test.teardown:
            raise AssertionError(f"Result test '{test.name}' not cleared")
    assert data.name == data.doc == result.name == 'Not visible in results'
    assert result.doc.endswith('[start suite]')
    assert result.metadata['suite'] == '[start]'
    assert result.metadata['tests'] == 'xxxxx'
    assert result.metadata['number'] == '42'
    result.name += ' [end suite]'
    result.doc += ' [end suite]'
    result.metadata['suite'] += ' [end]'
    for test in result.tests:
        test.name = 'Not visible in reports'
        test.status = 'PASS'    # Not visible in reports


def startTest(data, result):
    data.name = data.doc = result.name = 'Not visible in results'
    result.doc = (result.doc + ' [start test]').strip()
    result.tags.add('[start]')
    result.message = '[start]'
    result.parent.metadata['tests'] += 'x'
    data.body.create_keyword('No Operation')
    if data is data.parent.tests[-1] and 'dynamic' not in data.tags:
        new = data.parent.tests.create(name='Added by startTest',
                                       tags=['dynamic', 'start'])
        new.body.create_keyword(name='Fail', args=['Dynamically added!'])


def end_test(data, result):
    result.name = 'Does not go to output.xml'
    result.doc += ' [end test]'
    result.tags.add('[end]')
    result.passed = not result.passed
    result.message += ' [end]'
    if 'dynamic' in data.tags and 'start' in data.tags:
        new = data.parent.tests.create(name='Added by end_test',
                                       doc='Dynamic',
                                       tags=['dynamic', 'end'])
        new.body.create_keyword(name='Log', args=['Dynamically added!', 'INFO'])
    data.name = data.doc = 'Not visible in results'


def log_message(msg):
    msg.message = msg.message.upper()
    msg.timestamp = '2015-12-16 15:51:20.141'


message = log_message


def output_file(path):
    print(f"Output: {path.name}", file=sys.__stderr__)


def log_file(path):
    print(f"Log: {path.name}", file=sys.__stderr__)


def report_file(path):
    print(f"Report: {path.name}", file=sys.__stderr__)


def debug_file(path):
    print(f"Debug: {path.name}", file=sys.__stderr__)


def xunit_file(path):
    print(f"Xunit: {path.name}", file=sys.__stderr__)


def close():
    print("Close", file=sys.__stderr__)


class TestModifier(SuiteVisitor):

    def visit_test(self, test):
        test.name += ' [start suite]'
        test.doc = (test.doc + ' [start suite]').strip()
        test.tags.add('[start suite]')


def not_implemented(*args):
    raise SystemExit('Should not be called!')


library_import = resource_import = variables_import = not_implemented
