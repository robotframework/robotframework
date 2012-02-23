import unittest
from os.path import abspath, dirname, join, normpath

from robot.utils.asserts import assert_equals
from robot.testdoc import JsonConverter, TestSuiteFactory

DATADIR = join(dirname(abspath(__file__)), '..', '..', 'atest', 'testdata', 'misc')


class TestJsonConverter(unittest.TestCase):
    suite = None

    def setUp(self):
        if not self.suite:
            suite = TestSuiteFactory(DATADIR, doc='My doc', metadata=['a:b'])
            TestJsonConverter.suite = JsonConverter().convert(suite)

    def test_suite(self):
        self._verify(self.suite,
                     source=normpath(DATADIR),
                     id='s1',
                     name='Misc',
                     fullName='Misc',
                     doc='My doc',
                     metadata={'a': 'b'},
                     numberOfTests=161,
                     tests=[],
                     keywords=[])
        self._verify(self.suite['suites'][0],
                     source=join(normpath(DATADIR), 'dummy_lib_test.html'),
                     id='s1-s1',
                     name='Dummy Lib Test',
                     fullName='Misc.Dummy Lib Test',
                     doc='',
                     numberOfTests=1,
                     suites=[],
                     keywords=[])
        self._verify(self.suite['suites'][3]['suites'][1]['suites'][-1],
                     source=join(normpath(DATADIR), 'multiple_suites',
                                 '02__sub.suite.1', 'second__.Sui.te.2..html'),
                     id='s1-s4-s2-s2',
                     name='.Sui.te.2.',
                     fullName='Misc.Multiple Suites.Sub.Suite.1..Sui.te.2.',
                     doc='',
                     numberOfTests=12,
                     suites=[],
                     keywords=[])

    def test_test(self):
        self._verify(self.suite['suites'][0]['tests'][0],
                     id='s1-s1-t1',
                     name='Dummy Test',
                     fullName='Misc.Dummy Lib Test.Dummy Test',
                     doc='',
                     tags=[],
                     timeout='')
        self._verify(self.suite['suites'][2]['tests'][-1],
                     id='s1-s3-t5',
                     name='Fifth',
                     fullName='Misc.Many Tests.Fifth',
                     doc='',
                     tags=['d1', 'd2', 'f1'],
                     timeout='')
        self._verify(self.suite['suites'][-3]['tests'][0],
                     id='s1-s9-t1',
                     name='Default Test Timeout',
                     fullName='Misc.Timeouts.Default Test Timeout',
                     doc='I have a timeout',
                     tags=[],
                     timeout='1 minute 42 seconds')

    def test_timeout(self):
        self._verify(self.suite['suites'][-3]['tests'][0],
                     name='Default Test Timeout',
                     timeout='1 minute 42 seconds')
        self._verify(self.suite['suites'][-3]['tests'][1],
                     name='Test Timeout With Message',
                     timeout='1 day 2 hours :: The message')
        self._verify(self.suite['suites'][-3]['tests'][2],
                     name='Test Timeout With Variable',
                     timeout='${100}')

    def test_keyword(self):
        self._verify(self.suite['suites'][0]['tests'][0]['keywords'][0],
                     name='dummykw',
                     arguments='',
                     type='KEYWORD')
        self._verify(self.suite['suites'][2]['tests'][-1]['keywords'][0],
                     name='Log',
                     arguments='Test 5',
                     type='KEYWORD')

    def test_suite_setup_and_teardown(self):
        self._verify(self.suite['suites'][2]['keywords'][0],
                     name='Log',
                     arguments='Setup',
                     type='SETUP')
        self._verify(self.suite['suites'][2]['keywords'][1],
                     name='Noop',
                     arguments='',
                     type='TEARDOWN')

    def test_test_setup_and_teardown(self):
        self._verify(self.suite['suites'][6]['tests'][0]['keywords'][0],
                     name='Test Setup',
                     arguments='',
                     type='SETUP')
        self._verify(self.suite['suites'][6]['tests'][0]['keywords'][2],
                     name='Test Teardown',
                     arguments='',
                     type='TEARDOWN')

    def test_for_loops(self):
        self._verify(self.suite['suites'][1]['tests'][0]['keywords'][0],
                     name='${pet} IN [ cat | dog | horse ]',
                     arguments='',
                     type='FOR')
        self._verify(self.suite['suites'][1]['tests'][1]['keywords'][0],
                     name='${i} IN RANGE [ 10 ]',
                     arguments='',
                     type='FOR')

    def test_assign(self):
        self._verify(self.suite['suites'][-2]['tests'][0]['keywords'][1],
                     name='${msg} = Evaluate',
                     arguments="u'Fran\\\\xe7ais'",
                     type='KEYWORD')

    def _verify(self, item, **expected):
        for name in expected:
            assert_equals(item[name], expected[name])


if __name__ == '__main__':
    unittest.main()
