import base64
import unittest
import zlib
from os.path import abspath, basename, dirname, join

from robot.utils.asserts import assert_equal, assert_true
from robot.result import Keyword, Message, TestCase, TestSuite
from robot.result.executionerrors import ExecutionErrors
from robot.model import Statistics, BodyItem
from robot.reporting.jsmodelbuilders import (
    ErrorsBuilder, JsBuildingContext, KeywordBuilder, MessageBuilder,
    StatisticsBuilder, SuiteBuilder, TestBuilder
)
from robot.reporting.stringcache import StringIndex


CURDIR = dirname(abspath(__file__))


def decode_string(string):
    return zlib.decompress(base64.b64decode(string.encode('ASCII'))).decode('UTF-8')


def remap(model, strings):
    if isinstance(model, StringIndex):
        if strings[model].startswith('*'):
            # Strip the asterisk from a raw string.
            return strings[model][1:]
        return decode_string(strings[model])
    elif isinstance(model, (int, type(None))):
        return model
    elif isinstance(model, tuple):
        return tuple(remap(item, strings) for item in model)
    else:
        raise AssertionError("Item '%s' has invalid type '%s'" % (model, type(model)))


class TestBuildTestSuite(unittest.TestCase):

    def test_default_suite(self):
        self._verify_suite(TestSuite())

    def test_suite_with_values(self):
        suite = TestSuite('Name', 'Doc', {'m1': 'v1', 'M2': 'V2'}, None, 'Message',
                          '20111204 19:00:00.000', '20111204 19:00:42.001')
        self._verify_suite(suite, 'Name', 'Doc', ('m1', '<p>v1</p>', 'M2', '<p>V2</p>'),
                           message='Message', start=0, elapsed=42001)

    def test_relative_source(self):
        self._verify_suite(TestSuite(source='non-existing'), source='non-existing')
        source = join(CURDIR, 'test_jsmodelbuilders.py')
        self._verify_suite(TestSuite(source=source), source=source,
                           relsource=basename(source))

    def test_suite_html_formatting(self):
        self._verify_suite(TestSuite(name='*xxx*', doc='*bold* <&>',
                                     metadata={'*x*': '*b*', '<': '>'}),
                           name='*xxx*', doc='<b>bold</b> &lt;&amp;&gt;',
                           metadata=('*x*', '<p><b>b</b></p>', '&lt;', '<p>&gt;</p>'))

    def test_default_test(self):
        self._verify_test(TestCase())

    def test_test_with_values(self):
        test = TestCase('Name', '*Doc*', ['t1', 't2'], '1 minute', 'PASS', 'Msg',
                        '20111204 19:22:22.222', '20111204 19:22:22.333')
        test.setup.config(kwname='setup')
        test.teardown.config(kwname='td')
        k1 = self._verify_keyword(test.setup, type=1, kwname='setup')
        k2 = self._verify_keyword(test.teardown, type=2, kwname='td')
        self._verify_test(test, 'Name', '<b>Doc</b>', ('t1', 't2'),
                          '1 minute', 1, 'Msg', 0, 111, (k1, k2))

    def test_name_escaping(self):
        kw = Keyword('quote:"', 'and *url* https://url.com', '*"Doc"*',)
        self._verify_keyword(kw, 0, 'quote:&quot;', 'and *url* https://url.com', '<b>"Doc"</b>')
        test = TestCase('quote:" and *url* https://url.com', '*"Doc"*',)
        self._verify_test(test, 'quote:&quot; and *url* https://url.com', '<b>"Doc"</b>')
        suite = TestSuite('quote:" and *url* https://url.com', '*"Doc"*',)
        self._verify_suite(suite, 'quote:&quot; and *url* https://url.com', '<b>"Doc"</b>')

    def test_default_keyword(self):
        self._verify_keyword(Keyword())

    def test_keyword_with_values(self):
        kw = Keyword('KW Name', 'libname', 'http://doc', ('arg1', 'arg2'),
                     ('${v1}', '${v2}'), ('tag1', 'tag2'), '1 second', 'SETUP',
                     'PASS', '20111204 19:42:42.000', '20111204 19:42:42.042')
        self._verify_keyword(kw, 1, 'KW Name', 'libname',
                             '<a href="http://doc">http://doc</a>',
                             'arg1, arg2', '${v1}, ${v2}', 'tag1, tag2',
                             '1 second', 1, 0, 42)

    def test_default_message(self):
        self._verify_message(Message())
        self._verify_min_message_level('INFO')

    def test_message_with_values(self):
        msg = Message('Message', 'DEBUG', timestamp='20111204 22:04:03.210')
        self._verify_message(msg, 'Message', 1, 0)
        self._verify_min_message_level('DEBUG')

    def test_warning_linking(self):
        msg = Message('Message', 'WARN', timestamp='20111204 22:04:03.210',
                      parent=TestCase().body.create_keyword())
        self._verify_message(msg, 'Message', 3, 0)
        links = self.context._msg_links
        assert_equal(len(links), 1)
        key = (msg.message, msg.level, msg.timestamp)
        assert_equal(remap(links[key], self.context.strings), 't1-k1')

    def test_error_linking(self):
        msg = Message('ERROR Message', 'ERROR', timestamp='20150609 01:02:03.004',
                      parent=TestCase().body.create_keyword().body.create_keyword())
        self._verify_message(msg, 'ERROR Message', 4, 0)
        links = self.context._msg_links
        assert_equal(len(links), 1)
        key = (msg.message, msg.level, msg.timestamp)
        assert_equal(remap(links[key], self.context.strings), 't1-k1-k1')

    def test_message_with_html(self):
        self._verify_message(Message('<img>'), '&lt;img&gt;')
        self._verify_message(Message('<b></b>', html=True), '<b></b>')

    def test_nested_structure(self):
        suite = TestSuite()
        suite.setup.config(kwname='setup')
        suite.teardown.config(kwname='td')
        K1 = self._verify_keyword(suite.setup, type=1, kwname='setup')
        K2 = self._verify_keyword(suite.teardown, type=2, kwname='td')
        suite.suites = [TestSuite()]
        suite.suites[0].tests = [TestCase(tags=['crit', 'xxx'])]
        t = self._verify_test(suite.suites[0].tests[0], tags=('crit', 'xxx'))
        suite.tests = [TestCase(), TestCase(status='PASS')]
        S1 = self._verify_suite(suite.suites[0],
                                status=0, tests=(t,), stats=(1, 0, 1, 0))
        suite.tests[0].body = [Keyword(type=Keyword.FOR), Keyword()]
        suite.tests[0].body[0].body = [Keyword(type=Keyword.FOR_ITERATION), Message()]
        k = self._verify_keyword(suite.tests[0].body[0].body[0], type=4)
        m = self._verify_message(suite.tests[0].body[0].messages[0])
        k1 = self._verify_keyword(suite.tests[0].body[0], type=3, body=(k, m))
        suite.tests[0].body[1].body = [Message(), Message('msg', level='TRACE')]
        m1 = self._verify_message(suite.tests[0].body[1].messages[0])
        m2 = self._verify_message(suite.tests[0].body[1].messages[1], 'msg', level=0)
        k2 = self._verify_keyword(suite.tests[0].body[1], body=(m1, m2))
        T1 = self._verify_test(suite.tests[0], body=(k1, k2))
        T2 = self._verify_test(suite.tests[1], status=1)
        self._verify_suite(suite, status=0, keywords=(K1, K2), suites=(S1,),
                           tests=(T1, T2), stats=(3, 1, 2, 0))
        self._verify_min_message_level('TRACE')

    def test_timestamps(self):
        suite = TestSuite(starttime='20111205 00:33:33.333')
        suite.setup.config(kwname='s1', starttime='20111205 00:33:33.334')
        suite.setup.body.create_message('Message', timestamp='20111205 00:33:33.343')
        suite.setup.body.create_message(level='DEBUG', timestamp='20111205 00:33:33.344')
        suite.tests.create(starttime='20111205 00:33:34.333')
        context = JsBuildingContext()
        model = SuiteBuilder(context).build(suite)
        self._verify_status(model[5], start=0)
        self._verify_status(model[-2][0][8], start=1)
        self._verify_mapped(model[-2][0][-1], context.strings,
                            ((8, 10, 2, 'Message'), (8, 11, 1, '')))
        self._verify_status(model[-3][0][4], start=1000)

    def test_if(self):
        test = TestSuite().tests.create()
        test.body.create_if()
        test.body[0].body.create_branch(BodyItem.IF, '$x > 0', status='NOT RUN')
        test.body[0].body.create_branch(BodyItem.ELSE_IF, '$x < 0', status='PASS')
        test.body[0].body.create_branch(BodyItem.ELSE, status='NOT RUN')
        test.body[0].body[-1].body.create_keyword('z')
        exp_if = (
            5, '$x &gt; 0', '', '', '', '', '', '', (3, None, 0), ()
        )
        exp_else_if = (
            6, '$x &lt; 0', '', '', '', '', '', '', (1, None, 0), ()
        )
        exp_else = (
            7, '', '', '', '', '', '', '', (3, None, 0),
            ((0, 'z', '', '', '', '', '', '', (0, None, 0), ()),)
        )
        self._verify_test(test, body=(exp_if, exp_else_if, exp_else))

    def test_message_directly_under_test(self):
        test = TestSuite().tests.create()
        test.body.create_message('Hi from test')
        test.body.create_keyword().body.create_message('Hi from keyword')
        test.body.create_message('Hi from test again', 'WARN')
        exp_m1 = (8, None, 2, 'Hi from test')
        exp_kw = (0, '', '', '', '', '', '', '', (0, None, 0),
                  ((8, None, 2, 'Hi from keyword'),))
        exp_m3 = (8, None, 3, 'Hi from test again')
        self._verify_test(test, body=(exp_m1, exp_kw, exp_m3))

    def _verify_status(self, model, status=0, start=None, elapsed=0):
        assert_equal(model, (status, start, elapsed))

    def _verify_suite(self, suite, name='', doc='', metadata=(), source='',
                      relsource='', status=2, message='', start=None, elapsed=0,
                      suites=(), tests=(), keywords=(), stats=(0, 0, 0, 0)):
        status = (status, start, elapsed, message) \
                if message else (status, start, elapsed)
        doc = '<p>%s</p>' % doc if doc else ''
        return self._build_and_verify(SuiteBuilder, suite, name, source,
                                      relsource, doc, metadata, status,
                                      suites, tests, keywords, stats)

    def _get_status(self, *elements):
        return elements if elements[-1] else elements[:-1]

    def _verify_test(self, test, name='', doc='', tags=(), timeout='',
                     status=0, message='', start=None, elapsed=0, body=()):
        status = (status, start, elapsed, message) \
                if message else (status, start, elapsed)
        doc = '<p>%s</p>' % doc if doc else ''
        return self._build_and_verify(TestBuilder, test, name, timeout,
                                      doc, tags, status, body)

    def _verify_keyword(self, keyword, type=0, kwname='', libname='', doc='',
                        args='', assign='', tags='', timeout='', status=0,
                        start=None, elapsed=0, body=()):
        status = (status, start, elapsed)
        doc = '<p>%s</p>' % doc if doc else ''
        return self._build_and_verify(KeywordBuilder, keyword, type, kwname,
                                      libname, timeout, doc, args, assign, tags,
                                      status, body)

    def _verify_message(self, msg, message='', level=2, timestamp=None):
        return self._build_and_verify(MessageBuilder, msg, 8, timestamp, level, message)

    def _verify_min_message_level(self, expected):
        assert_equal(self.context.min_level, expected)

    def _build_and_verify(self, builder_class, item, *expected):
        self.context = JsBuildingContext(log_path=join(CURDIR, 'log.html'))
        model = builder_class(self.context).build(item)
        self._verify_mapped(model, self.context.strings, expected)
        return expected

    def _verify_mapped(self, model, strings, expected):
        mapped_model = tuple(remap(model, strings))
        assert_equal(mapped_model, expected)


class TestSplitting(unittest.TestCase):

    def test_test_keywords(self):
        suite = self._get_suite_with_tests()
        expected, _ = self._build_and_remap(suite)
        expected_split = [expected[-3][0][-1], expected[-3][1][-1]]
        expected[-3][0][-1], expected[-3][1][-1] = 1, 2
        model, context = self._build_and_remap(suite, split_log=True)
        assert_equal(context.strings, ('*', '*suite', '*t1', '*t2'))
        assert_equal(model, expected)
        assert_equal([strings for _, strings in context.split_results],
                      [('*', '*t1-k1', '*t1-k1-k1', '*t1-k2'), ('*', '*t2-k1')])
        assert_equal([self._to_list(remap(*res)) for res in context.split_results],
                      expected_split)

    def _get_suite_with_tests(self):
        suite = TestSuite(name='suite')
        suite.tests = [TestCase('t1'), TestCase('t2')]
        suite.tests[0].body = [Keyword('t1-k1'), Keyword('t1-k2')]
        suite.tests[0].body[0].body = [Keyword('t1-k1-k1')]
        suite.tests[1].body = [Keyword('t2-k1')]
        return suite

    def _build_and_remap(self, suite, split_log=False):
        context = JsBuildingContext(split_log=split_log)
        model = remap(SuiteBuilder(context).build(suite), context.strings)
        return self._to_list(model), context

    def _to_list(self, model):
        return list(self._to_list(item) if isinstance(item, tuple) else item
                    for item in model)

    def test_suite_keywords(self):
        suite = self._get_suite_with_keywords()
        expected, _ = self._build_and_remap(suite)
        expected_split = [expected[-2][0][-1], expected[-2][1][-1]]
        expected[-2][0][-1], expected[-2][1][-1] = 1, 2
        model, context = self._build_and_remap(suite, split_log=True)
        assert_equal(context.strings, ('*', '*root', '*k1', '*k2'))
        assert_equal(model, expected)
        assert_equal([strings for _, strings in context.split_results],
                     [('*', '*k1-k2'), ('*',)])
        assert_equal([self._to_list(remap(*res)) for res in context.split_results],
                     expected_split)

    def _get_suite_with_keywords(self):
        suite = TestSuite(name='root')
        suite.setup.config(kwname='k1')
        suite.teardown.config(kwname='k2')
        suite.setup.body.create_keyword('k1-k2')
        return suite

    def test_nested_suite_and_test_keywords(self):
        suite = self._get_nested_suite_with_tests_and_keywords()
        expected, _ = self._build_and_remap(suite)
        expected_split = [expected[-4][0][-3][0][-1], expected[-4][0][-3][1][-1],
                          expected[-4][1][-3][0][-1], expected[-4][1][-2][0][-1],
                          expected[-2][0][-1], expected[-2][1][-1]]
        (expected[-4][0][-3][0][-1], expected[-4][0][-3][1][-1],
         expected[-4][1][-3][0][-1], expected[-4][1][-2][0][-1],
         expected[-2][0][-1], expected[-2][1][-1]) = 1, 2, 3, 4, 5, 6
        model, context = self._build_and_remap(suite, split_log=True)
        assert_equal(model, expected)
        assert_equal([self._to_list(remap(*res)) for res in context.split_results],
                      expected_split)

    def _get_nested_suite_with_tests_and_keywords(self):
        suite = self._get_suite_with_keywords()
        sub = TestSuite(name='suite2')
        suite.suites = [self._get_suite_with_tests(), sub]
        sub.setup.config(kwname='kw')
        sub.setup.body.create_keyword('skw').body.create_message('Message')
        sub.tests.create('test', doc='tdoc').body.create_keyword('koowee', doc='kdoc')
        return suite

    def test_message_linking(self):
        suite = self._get_suite_with_keywords()
        msg1 = suite.setup.body[0].body.create_message(
            'Message 1', 'WARN', timestamp='20111204 22:04:03.210'
        )
        msg2 = suite.tests.create().body.create_keyword().body.create_message(
            'Message 2', 'ERROR', timestamp='20111204 22:04:04.210'
        )
        context = JsBuildingContext(split_log=True)
        SuiteBuilder(context).build(suite)
        errors = ErrorsBuilder(context).build(ExecutionErrors([msg1, msg2]))
        assert_equal(remap(errors, context.strings),
                     ((8, -1000, 3, 'Message 1', 's1-k1-k1'),
                      (8, 0, 4, 'Message 2', 's1-t1-k1')))
        assert_equal(remap(context.link(msg1), context.strings), 's1-k1-k1')
        assert_equal(remap(context.link(msg2), context.strings), 's1-t1-k1')
        assert_true('*s1-k1-k1' in context.strings)
        assert_true('*s1-t1-k1' in context.strings)
        for res in context.split_results:
            assert_true('*s1-k1-k1' not in res[1])
            assert_true('*s1-t1-k1' not in res[1])


class TestPruneInput(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite()
        self.suite.setup.config(kwname='s')
        self.suite.teardown.config(kwname='t')
        s1 = self.suite.suites.create()
        s1.setup.config(kwname='s1')
        tc = s1.tests.create()
        tc.setup.config(kwname='tcs')
        tc.teardown.config(kwname='tct')
        tc.body = [Keyword(), Keyword(), Keyword()]
        tc.body[0].body = [Keyword(), Keyword(), Message(), Message(), Message()]
        tc.body[0].teardown.config(kwname='kt')
        s2 = self.suite.suites.create()
        t1 = s2.tests.create()
        t2 = s2.tests.create()
        t1.body = [Keyword()]
        t2.body = [Keyword(), Keyword()]

    def test_no_pruning(self):
        SuiteBuilder(JsBuildingContext(prune_input=False)).build(self.suite)
        assert_equal(self.suite.setup.kwname, 's')
        assert_equal(self.suite.teardown.kwname, 't')
        assert_equal(self.suite.suites[0].setup.kwname, 's1')
        assert_equal(self.suite.suites[0].teardown.kwname, None)
        assert_equal(self.suite.suites[0].tests[0].setup.kwname, 'tcs')
        assert_equal(self.suite.suites[0].tests[0].teardown.kwname, 'tct')
        assert_equal(len(self.suite.suites[0].tests[0].body), 3)
        assert_equal(len(self.suite.suites[0].tests[0].body[0].body), 5)
        assert_equal(len(self.suite.suites[0].tests[0].body[0].messages), 3)
        assert_equal(self.suite.suites[0].tests[0].body[0].teardown.kwname, 'kt')
        assert_equal(len(self.suite.suites[1].tests[0].body), 1)
        assert_equal(len(self.suite.suites[1].tests[1].body), 2)

    def test_prune_suites_from_suite(self):
        suite = self.suite
        assert_equal(len(suite.suites), 2)
        assert_equal(len(suite.tests), 0)
        SuiteBuilder(JsBuildingContext(prune_input=True)).build(suite)
        assert_equal(len(suite.suites), 0)
        assert_equal(len(suite.tests), 0)

    def test_prune_test_from_suite(self):
        suite = self.suite.suites[0]
        assert_equal(len(suite.suites), 0)
        assert_equal(len(suite.tests), 1)
        SuiteBuilder(JsBuildingContext(prune_input=True)).build(suite)
        assert_equal(len(suite.suites), 0)
        assert_equal(len(suite.tests), 0)

    def test_prune_test(self):
        test = self.suite.suites[0].tests[0]
        assert_equal(len(test.body), 3)
        TestBuilder(JsBuildingContext(prune_input=True)).build(test)
        assert_equal(len(test.body), 0)

    def test_prune_keyword(self):
        kw = self.suite.suites[0].tests[0].body[0]
        assert_equal(len(kw.body), 5)
        assert_equal(len(kw.messages), 3)
        KeywordBuilder(JsBuildingContext(prune_input=True)).build(kw)
        assert_equal(len(kw.body), 0)
        assert_equal(len(kw.messages), 0)

    def test_prune_errors(self):
        errors = ExecutionErrors([Message(), Message()])
        ErrorsBuilder(JsBuildingContext(prune_input=False)).build(errors)
        assert_equal(len(errors), 2)
        ErrorsBuilder(JsBuildingContext(prune_input=True)).build(errors)
        assert_equal(len(errors), 0)


class TestBuildStatistics(unittest.TestCase):

    def test_total_stats(self):
        all = self._build_statistics()[0][0]
        self._verify_stat(all, 2, 2, 1, 'All Tests', '00:00:33')

    def test_tag_stats(self):
        stats = self._build_statistics()[1]
        comb, t1, t2, t3 = self._build_statistics()[1]
        self._verify_stat(t2, 2, 0, 0, 't2', '00:00:22',
                          doc='doc', links='t:url')
        self._verify_stat(comb, 2, 0, 0, 'name', '00:00:22',
                          info='combined', combined='t1&amp;t2')
        self._verify_stat(t1, 2, 2, 0, 't1', '00:00:33')
        self._verify_stat(t3, 0, 1, 1, 't3', '00:00:01')

    def test_suite_stats(self):
        root, sub1, sub2 = self._build_statistics()[2]
        self._verify_stat(root, 2, 2, 1, 'root', '00:00:42', name='root', id='s1')
        self._verify_stat(sub1, 1, 1, 1, 'root.sub1', '00:00:10', name='sub1', id='s1-s1')
        self._verify_stat(sub2, 1, 1, 0, 'root.sub2', '00:00:30', name='sub2', id='s1-s2')

    def _build_statistics(self):
        return StatisticsBuilder().build(self._get_statistics())

    def _get_statistics(self):
        return Statistics(self._get_suite(),
                          suite_stat_level=2,
                          tag_stat_combine=[('t1&t2', 'name')],
                          tag_doc=[('t2', 'doc')],
                          tag_stat_link=[('?2', 'url', '%1')])

    def _get_suite(self):
        ts = lambda s, ms=0: '20120816 16:09:%02d.%03d' % (s, ms)
        suite = TestSuite(name='root', starttime=ts(0), endtime=ts(42))
        sub1 = TestSuite(name='sub1', starttime=ts(0), endtime=ts(10))
        sub2 = TestSuite(name='sub2')
        suite.suites = [sub1, sub2]
        sub1.tests = [
            TestCase(tags=['t1', 't2'], status='PASS', starttime=ts(0), endtime=ts(1, 500)),
            TestCase(tags=['t1', 't3'], status='FAIL', starttime=ts(2), endtime=ts(3, 499)),
            TestCase(tags=['t3'], status='SKIP', starttime=ts(3, 560), endtime=ts(3, 560))
        ]
        sub2.tests = [
            TestCase(tags=['t1', 't2'], status='PASS', starttime=ts(10), endtime=ts(30))
        ]
        sub2.suites.create(name='below suite stat level')\
                .tests.create(tags=['t1'], status='FAIL', starttime=ts(30), endtime=ts(40))
        return suite

    def _verify_stat(self, stat, pass_, fail, skip, label, elapsed, **attrs):
        attrs.update({'pass': pass_, 'fail': fail, 'skip': skip,
                      'label': label, 'elapsed': elapsed})
        assert_equal(stat, attrs)


class TestBuildErrors(unittest.TestCase):

    def setUp(self):
        msgs = [Message('Error', 'ERROR', timestamp='20111206 14:33:00.000'),
                Message('Warning', 'WARN', timestamp='20111206 14:33:00.042')]
        self.errors = ExecutionErrors(msgs)

    def test_errors(self):
        context = JsBuildingContext()
        model = ErrorsBuilder(context).build(self.errors)
        model = remap(model, context.strings)
        assert_equal(model, ((8, 0, 4, 'Error'), (8, 42, 3, 'Warning')))

    def test_linking(self):
        self.errors.messages.create('Linkable', 'WARN',
                                    timestamp='20111206 14:33:00.001')
        context = JsBuildingContext()
        msg = TestSuite().tests.create().body.create_keyword().body.create_message(
            'Linkable', 'WARN', timestamp='20111206 14:33:00.001'
        )
        MessageBuilder(context).build(msg)
        model = ErrorsBuilder(context).build(self.errors)
        model = remap(model, context.strings)
        assert_equal(model, ((8, -1, 4, 'Error'),
                             (8, 41, 3, 'Warning'),
                             (8, 0, 3, 'Linkable', 's1-t1-k1')))


if __name__ == '__main__':
    unittest.main()
