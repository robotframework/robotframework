import sys
import os.path

from robot.api import SuiteVisitor
from robot.utils.asserts import assert_equal


def start_suite(data, result):
    data.name = data.doc = result.name = 'Not visible in results'
    result.doc = (result.doc + ' [start suite]').strip()
    result.metadata['suite'] = '[start]'
    result.metadata['tests'] = ''
    result.metadata['number'] = 42
    assert_equal(len(data.tests), 2)
    assert_equal(len(result.tests), 0)
    data.tests.create(name='Added by start_suite')
    data.visit(TestModifier())


def end_suite(data, result):
    assert_equal(len(data.tests), 5)
    assert_equal(len(result.tests), 5)
    for test in result.tests:
        if test.setup or test.body or test.teardown:
            raise AssertionError(f"Result test '{test.name}' not cleared")
    assert data.name == data.doc == result.name == 'Not visible in results'
    assert result.doc.endswith('[start suite]')
    assert_equal(result.metadata['suite'],'[start]')
    assert_equal(result.metadata['tests'], 'xxxxx')
    assert_equal(result.metadata['number'], '42')
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
    if msg.message == 'Hello says "Fail"!' or msg.level == 'TRACE':
        msg.message = None
    else:
        msg.message = msg.message.upper()
        msg.timestamp = '2015-12-16 15:51:20.141'


message = log_message


def output_file(path):
    name = path.name if path is not None else 'None'
    print(f"Output: {name}", file=sys.__stderr__)


def log_file(path):
    print(f"Log: {path.name}", file=sys.__stderr__)


def report_file(path):
    print(f"Report: {path.name}", file=sys.__stderr__)


def debug_file(path):
    print(f"Debug: {path.name}", file=sys.__stderr__)


def xunit_file(path):
    print(f"Xunit: {path.name}", file=sys.__stderr__)


def library_import(library, importer):
    if library.name == 'BuiltIn':
        library.find_keywords('Log', count=1).doc = 'Changed!'
        assert_equal(importer.name, 'BuiltIn')
        assert_equal(importer.args, ())
        assert_equal(importer.source, None)
        assert_equal(importer.lineno, None)
        assert_equal(importer.owner, None)
    else:
        assert_equal(library.name, 'String')
        assert_equal(importer.name, 'String')
        assert_equal(importer.args, ())
        assert_equal(importer.source.name, 'pass_and_fail.robot')
        assert_equal(importer.lineno, 5)
    print(f"Imported library '{library.name}' with {len(library.keywords)} keywords.")


def resource_import(resource, importer):
    assert_equal(resource.name, 'example')
    assert_equal(resource.source.name, 'example.resource')
    assert_equal(importer.name, 'example.resource')
    assert_equal(importer.args, ())
    assert_equal(importer.source.name, 'pass_and_fail.robot')
    assert_equal(importer.lineno, 6)
    kw = resource.find_keywords('Resource Keyword', count=1)
    kw.body.create_keyword('New!')
    new = resource.keywords.create('New!', doc='Dynamically created.')
    new.body.create_keyword('Log', ['Hello, new keyword!'])
    print(f"Imported resource '{resource.name}' with {len(resource.keywords)} keywords.")


def variables_import(attrs, importer):
    assert_equal(attrs['name'], 'variables.py')
    assert_equal(attrs['args'], ['arg 1'])
    assert_equal(os.path.basename(attrs['source']), 'variables.py')
    assert_equal(importer.name, 'variables.py')
    assert_equal(importer.args, ('arg ${1}',))
    assert_equal(importer.source.name, 'pass_and_fail.robot')
    assert_equal(importer.lineno, 7)
    assert_equal(importer.owner.owner.source.name, 'pass_and_fail.robot')
    print(f"Imported variables '{attrs['name']}' without much info.")


def close():
    print("Close", file=sys.__stderr__)


class TestModifier(SuiteVisitor):

    def visit_test(self, test):
        test.name += ' [start suite]'
        test.doc = (test.doc + ' [start suite]').strip()
        test.tags.add('[start suite]')
