import unittest
from os.path import abspath, dirname, join, normpath

from robot.utils.asserts import assert_equals
from robot.result import ResultFromXml, TestSuite, TestCase, Keyword, Message
from robot.reporting.jsmodelbuilders import *
from robot.reporting.parsingcontext import TextIndex as StringIndex

CURDIR = dirname(abspath(__file__))


def get_status(*elements):
    return elements if elements[-1] else elements[:-1]


class TestBuildTestSuite(unittest.TestCase):

    def test_default_suite(self):
        self._verify_suite(TestSuite())

    def test_suite_with_values(self):
        suite = TestSuite('', 'Name', 'Doc', {'m1': 'v1', 'm2': 'v2'}, 'Message',
                          '20111204 19:00:00.000', '20111204 19:00:42.001')
        self._verify_suite(suite, 'Name', 'Doc', ('m1', 'v1', 'm2', 'v2'),
                           message='Message', start=0, elapsed=42001)

    def test_relative_source(self):
        self._verify_suite(TestSuite(source='non-existing'), source='non-existing')
        self._verify_suite(TestSuite(source=__file__), source=__file__,
                           relsource=os.path.basename(__file__))

    def test_default_test(self):
        self._verify_test(TestCase())

    def test_test_with_values(self):
        test = TestCase('Name', 'Doc', ['t1', 't2'], '1 minute', 'PASS', 'Msg',
                        '20111204 19:22:22.222', '20111204 19:22:22.333')
        self._verify_test(test, 'Name', 'Doc', ('t1', 't2'), 1, '1 minute', 1,
                          'Msg', 0, 111)

    def test_default_keyword(self):
        self._verify_keyword(Keyword())

    def test_keyword_with_values(self):
        kw = Keyword('Name', 'Doc', ['a1', 'a2'], 'setup', '1 second', 'PASS',
                     '20111204 19:42:42.000', '20111204 19:42:42.042')
        self._verify_keyword(kw, 1, 'Name', 'Doc', 'a1, a2', '1 second', 1,
                             0, 42)

    def test_default_message(self):
        self._verify_message(Message())

    def test_message_with_values(self):
        msg = Message('Message', 'WARN', timestamp='20111204 22:04:03.210')
        self._verify_message(msg, 'Message', 3, 0)

    def test_message_with_html(self):
        self._verify_message(Message('<img>'), '&lt;img&gt;')
        self._verify_message(Message('<img>', html=True), '<img>')

    def test_nested_structure(self):
        suite = TestSuite()
        suite.set_criticality(critical_tags=['crit'])
        suite.keywords = [Keyword(type='setup'), Keyword(type='teardown')]
        K1 = self._verify_keyword(suite.keywords[0], type=1)
        K2 = self._verify_keyword(suite.keywords[1], type=2)
        suite.suites = [TestSuite()]
        suite.suites[0].tests = [TestCase(tags=['crit', 'xxx'])]
        t = self._verify_test(suite.suites[0].tests[0], tags=('crit', 'xxx'))
        suite.tests = [TestCase(), TestCase(status='PASS')]
        S1 = self._verify_suite(suite.suites[0],
                                status=0, tests=(t,), stats=(1, 0, 1, 0))
        suite.tests[0].keywords = [Keyword(type='for'), Keyword()]
        suite.tests[0].keywords[0].keywords = [Keyword(type='foritem')]
        suite.tests[0].keywords[0].messages = [Message()]
        k = self._verify_keyword(suite.tests[0].keywords[0].keywords[0], type=4)
        m = self._verify_message(suite.tests[0].keywords[0].messages[0])
        k1 = self._verify_keyword(suite.tests[0].keywords[0],
                                  type=3, keywords=(k,), messages=(m,))
        suite.tests[0].keywords[1].messages = [Message(), Message('msg')]
        m1 = self._verify_message(suite.tests[0].keywords[1].messages[0])
        m2 = self._verify_message(suite.tests[0].keywords[1].messages[1], 'msg')
        k2 = self._verify_keyword(suite.tests[0].keywords[1], messages=(m1, m2))
        T1 = self._verify_test(suite.tests[0], critical=0, keywords=(k1, k2))
        T2 = self._verify_test(suite.tests[1], critical=0, status=1)
        self._verify_suite(suite, status=0, keywords=(K1, K2), suites=(S1,),
                           tests=(T1, T2), stats=(3, 1, 1, 0))

    def test_timestamps(self):
        suite = TestSuite(starttime='20111205 00:33:33.333')
        suite.keywords.create(starttime='20111205 00:33:33.334')
        suite.keywords[0].messages.create('Message', timestamp='20111205 00:33:33.343')
        suite.keywords[0].messages.create(level='DEBUG', timestamp='20111205 00:33:33.344')
        suite.tests.create(starttime='20111205 00:33:34.333')
        builder = JsModelBuilder()
        model = builder._build_suite(suite)
        self._verify_status(model[5], start=0)
        self._verify_status(model[-2][0][5], start=1)
        self._verify_mapped(model[-2][0][-1], builder.dump_strings(),
                            ((10, 2, 'Message'), (11, 1, '')))
        self._verify_status(model[-3][0][5], start=1000)

    def _verify_status(self, model, status=0, start=None, elapsed=0):
        assert_equals(model, (status, start, elapsed))

    def _verify_suite(self, suite, name='', doc='', metadata=(), source='',
                      relsource='', status=1, message='', start=None, elapsed=0,
                      suites=(), tests=(), keywords=(), stats=(0, 0, 0, 0)):
        return self._build_and_verify('suite', suite, name, source, relsource,
                                      doc, metadata,
                                      get_status(status, start, elapsed, message),
                                      suites, tests, keywords, stats)

    def _verify_test(self, test, name='', doc='', tags=(), critical=1, timeout='',
                     status=0, message='', start=None, elapsed=0, keywords=()):
        return self._build_and_verify('test', test, name, timeout, critical, doc, tags,
                                      get_status(status, start, elapsed, message),
                                      keywords)

    def _verify_keyword(self, keyword, type=0, name='', doc='', args='',  timeout='',
                        status=0, start=None, elapsed=0, keywords=(), messages=()):
        return self._build_and_verify('keyword', keyword, type, name, timeout,
                                      doc, args, (status, start, elapsed),
                                      keywords, messages)

    def _verify_message(self, msg, message='', level=2, timestamp=None):
        return self._build_and_verify('message', msg, timestamp, level, message)

    def _build_and_verify(self, type, item, *expected):
        builder = JsModelBuilder(log_path=join(CURDIR, 'log.html'))
        model = getattr(builder, '_build_'+type)(item)
        self._verify_mapped(model, builder.dump_strings(), expected)
        return expected

    def _verify_mapped(self, model, strings, expected):
        mapped_model = tuple(self._map_strings(model, strings))
        assert_equals(mapped_model, expected)

    def _map_strings(self, model, strings):
        for item in model:
            if isinstance(item, StringIndex):
                yield strings[item][1:]
            elif isinstance(item, (int, long, type(None))):
                yield item
            elif isinstance(item, tuple):
                yield tuple(self._map_strings(item, strings))
            else:
                raise AssertionError("Item '%s' has invalid type '%s'" % (item, type(item)))


if __name__ == '__main__':
    unittest.main()
