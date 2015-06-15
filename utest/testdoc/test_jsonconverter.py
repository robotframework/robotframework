import unittest
from os.path import abspath, dirname, join, normpath

from robot.utils.asserts import assert_equals
from robot.testdoc import JsonConverter, TestSuiteFactory

DATADIR = join(dirname(abspath(__file__)), '..', '..', 'atest', 'testdata', 'misc')


def test_convert(item, **expected):
    for name in expected:
        assert_equals(item[name], expected[name])


class TestJsonConverter(unittest.TestCase):
    suite = None

    def setUp(self):
        if not self.suite:
            suite = TestSuiteFactory(DATADIR, doc='My doc', metadata=['abc:123', '1:2'])
            output = join(DATADIR, '..', 'output.html')
            self.__class__.suite = JsonConverter(output).convert(suite)

    def test_suite(self):
        test_convert(self.suite,
                     source=normpath(DATADIR),
                     relativeSource='misc',
                     id='s1',
                     name='Misc',
                     fullName='Misc',
                     doc='<p>My doc</p>',
                     metadata=[('1', '<p>2</p>'), ('abc', '<p>123</p>')],
                     numberOfTests=176,
                     tests=[],
                     keywords=[])
        test_convert(self.suite['suites'][0],
                     source=join(normpath(DATADIR), 'dummy_lib_test.robot'),
                     relativeSource='misc/dummy_lib_test.robot',
                     id='s1-s1',
                     name='Dummy Lib Test',
                     fullName='Misc.Dummy Lib Test',
                     doc='',
                     metadata=[],
                     numberOfTests=1,
                     suites=[],
                     keywords=[])
        test_convert(self.suite['suites'][4]['suites'][1]['suites'][-1],
                     source=join(normpath(DATADIR), 'multiple_suites',
                                 '02__sub.suite.1', 'second__.Sui.te.2..robot'),
                     relativeSource='misc/multiple_suites/02__sub.suite.1/second__.Sui.te.2..robot',
                     id='s1-s5-s2-s2',
                     name='.Sui.te.2.',
                     fullName='Misc.Multiple Suites.Sub.Suite.1..Sui.te.2.',
                     doc='',
                     metadata=[],
                     numberOfTests=12,
                     suites=[],
                     keywords=[])

    def test_multi_suite(self):
        data = TestSuiteFactory([join(DATADIR, 'normal.robot'),
                                 join(DATADIR, 'pass_and_fail.robot')])
        suite = JsonConverter().convert(data)
        test_convert(suite,
                     source='',
                     relativeSource='',
                     id='s1',
                     name='Normal &amp; Pass And Fail',
                     fullName='Normal &amp; Pass And Fail',
                     doc='',
                     metadata=[],
                     numberOfTests=4,
                     keywords=[],
                     tests=[])
        test_convert(suite['suites'][0],
                     source=normpath(join(DATADIR, 'normal.robot')),
                     relativeSource='',
                     id='s1-s1',
                     name='Normal',
                     fullName='Normal &amp; Pass And Fail.Normal',
                     doc='<p>Normal test cases</p>',
                     metadata=[('Something', '<p>My Value</p>')],
                     numberOfTests=2)
        test_convert(suite['suites'][1],
                     source=normpath(join(DATADIR, 'pass_and_fail.robot')),
                     relativeSource='',
                     id='s1-s2',
                     name='Pass And Fail',
                     fullName='Normal &amp; Pass And Fail.Pass And Fail',
                     doc='<p>Some tests here</p>',
                     metadata=[],
                     numberOfTests=2)

    def test_test(self):
        test_convert(self.suite['suites'][0]['tests'][0],
                     id='s1-s1-t1',
                     name='Dummy Test',
                     fullName='Misc.Dummy Lib Test.Dummy Test',
                     doc='',
                     tags=[],
                     timeout='')
        test_convert(self.suite['suites'][3]['tests'][-1],
                     id='s1-s4-t5',
                     name='Fifth',
                     fullName='Misc.Many Tests.Fifth',
                     doc='',
                     tags=['d1', 'd2', 'f1'],
                     timeout='')
        test_convert(self.suite['suites'][-3]['tests'][0],
                     id='s1-s10-t1',
                     name='Default Test Timeout',
                     fullName='Misc.Timeouts.Default Test Timeout',
                     doc='<p>I have a timeout</p>',
                     tags=[],
                     timeout='1 minute 42 seconds')

    def test_timeout(self):
        test_convert(self.suite['suites'][-3]['tests'][0],
                     name='Default Test Timeout',
                     timeout='1 minute 42 seconds')
        test_convert(self.suite['suites'][-3]['tests'][1],
                     name='Test Timeout With Message',
                     timeout='1 day 2 hours :: The message')
        test_convert(self.suite['suites'][-3]['tests'][2],
                     name='Test Timeout With Variable',
                     timeout='${100}')

    def test_keyword(self):
        test_convert(self.suite['suites'][0]['tests'][0]['keywords'][0],
                     name='dummykw',
                     arguments='',
                     type='KEYWORD')
        test_convert(self.suite['suites'][3]['tests'][-1]['keywords'][0],
                     name='Log',
                     arguments='Test 5',
                     type='KEYWORD')

    def test_suite_setup_and_teardown(self):
        test_convert(self.suite['suites'][3]['keywords'][0],
                     name='Log',
                     arguments='Setup',
                     type='SETUP')
        test_convert(self.suite['suites'][3]['keywords'][1],
                     name='No operation',
                     arguments='',
                     type='TEARDOWN')

    def test_test_setup_and_teardown(self):
        test_convert(self.suite['suites'][7]['tests'][0]['keywords'][0],
                     name='${TEST SETUP}',
                     arguments='',
                     type='SETUP')
        test_convert(self.suite['suites'][7]['tests'][0]['keywords'][2],
                     name='${TEST TEARDOWN}',
                     arguments='',
                     type='TEARDOWN')

    def test_for_loops(self):
        test_convert(self.suite['suites'][1]['tests'][0]['keywords'][0],
                     name='${pet} IN [ cat | dog | horse ]',
                     arguments='',
                     type='FOR')
        test_convert(self.suite['suites'][1]['tests'][1]['keywords'][0],
                     name='${i} IN RANGE [ 10 ]',
                     arguments='',
                     type='FOR')

    def test_assign(self):
        test_convert(self.suite['suites'][-2]['tests'][1]['keywords'][0],
                     name='${msg} = Evaluate',
                     arguments="u'Fran\\\\xe7ais'",
                     type='KEYWORD')


class TestFormattingAndEscaping(unittest.TestCase):
    suite = None

    def setUp(self):
        if not self.suite:
            suite = TestSuiteFactory(join(DATADIR, 'formatting_and_escaping.robot'),
                                     name='<suite>', metadata=['CLI>:*bold*'])
            self.__class__.suite = JsonConverter().convert(suite)

    def test_suite_documentation(self):
        test_convert(self.suite,
                     doc='''\
<p>We have <i>formatting</i> and &lt;escaping&gt;.</p>
<table border="1">
<tr>
<td><b>Name</b></td>
<td><b>URL</b></td>
</tr>
<tr>
<td>Robot</td>
<td><a href="http://robotframework.org">http://robotframework.org</a></td>
</tr>
<tr>
<td>Custom</td>
<td><a href="http://robotframework.org">link</a></td>
</tr>
</table>''')

    def test_suite_metadata(self):
        test_convert(self.suite,
                     metadata=[('CLI&gt;', '<p><b>bold</b></p>'),
                               ('Escape', '<p>this is &lt;b&gt;not bold&lt;/b&gt;</p>'),
                               ('Format', '<p>this is <b>bold</b></p>')])

    def test_test_documentation(self):
        test_convert(self.suite['tests'][0],
                     doc='<p><b>I</b> can haz <i>formatting</i> &amp; &lt;escaping&gt;!!</p>'
                         '\n<ul>\n<li>list</li>\n<li>here</li>\n</ul>')

    def test_escaping(self):
        test_convert(self.suite, name='&lt;suite&gt;')
        test_convert(self.suite['tests'][1],
            name='&lt;Escaping&gt;',
            tags=['*not bold*', '&lt;b&gt;not bold either&lt;/b&gt;'],
            keywords=[{'type': 'KEYWORD',
                       'name': '&lt;blink&gt;NO&lt;/blink&gt;',
                       'arguments': '&lt;&amp;&gt;'}])


if __name__ == '__main__':
    unittest.main()
