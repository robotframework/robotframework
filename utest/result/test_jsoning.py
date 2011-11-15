import unittest
from robot import utils
from robot.result.executionresult import ExecutionResult
from robot.result.keyword import Keyword
from robot.model.message import Message
from robot.output.loggerhelper import LEVELS
from robot.reporting.parsingcontext import Context
from robot.result.datamodel import DatamodelVisitor
from robot.result.jsondatamodelhandlers import _Handler, KeywordHandler, _StatusHandler
from robot.result.testcase import TestCase
from robot.result.testsuite import TestSuite
from robot.utils.asserts import assert_equals


class _PartialDatamodelVisitor(DatamodelVisitor):

    def __init__(self):
        self._elements = []
        self._context = Context()
        self._elements.append(_Handler(self._context))


class TestJsoning(unittest.TestCase):

    def setUp(self):
        self._visitor = _PartialDatamodelVisitor()
        self._context = self._visitor._context

    @property
    def datamodel(self):
        return self._visitor.datamodel

    def test_html_message_to_json(self):
        message = Message(message='<b>Great danger!</b>',
                          level='WARN',
                          html=True,
                          timestamp='20121212 12:12:12.121')
        message.visit(self._visitor)
        self._verify_message(self._visitor.datamodel[0], message)

    def _verify_message(self, message_json, message):
        assert_equals(message_json[0], self._context.timestamp(message.timestamp))
        assert_equals(message_json[1], LEVELS[message.level])
        message_text = message.message
        if not message.html:
            message_text = utils.html_escape(message_text)
        self._assert_text(message_json[2], message_text)

    def _assert_text(self, text_index, text):
        assert_equals(text_index, self._context.get_id(text))

    def test_non_html_message_to_json(self):
        message = Message(message='This is an html mark --> <html>',
                          level='INFO',
                          timestamp='19991211 12:12:12.821')
        message.visit(self._visitor)
        self._verify_message(self.datamodel[0], message)

    def test_times(self):
        for timestamp in ['20110531 12:48:09.020','N/A','20110531 12:48:09.010','20110531 12:48:19.035']:
            Message(timestamp=timestamp).visit(self._visitor)
        for index, millis in enumerate([0, None, -10, 10015]):
            assert_equals(self.datamodel[index][0], millis)

    def test_keyword_jsoning(self):
        self._context.start_suite()
        keyword = Keyword(name='Keyword Name',
                          doc='Documentation for <b>a keyword</b>',
                          args=['${first}', '${second}', '${third}'],
                          type='setup',
                          timeout='2 seconds',
                          status='PASS',
                          starttime='20110101 16:16:16.100',
                          endtime='20110101 16:16:18.161')
        keyword.messages.create(message='keyword message',
                                level='INFO',
                                timestamp='20110101 16:16:16.161')
        keyword.keywords.create(name='No Operation',
                                type='kw',
                                status='PASS')
        keyword.visit(self._visitor)
        self._verify_keyword(self.datamodel[0], keyword)

    def _verify_keyword(self, keyword_json, keyword):
        assert_equals(keyword_json[0], KeywordHandler._types[keyword.type])
        self._assert_texts(keyword_json, {1:keyword.name,
                                          2:keyword.timeout,
                                          4: ', '.join(keyword.args)})
        self._assert_html_text(keyword_json[3], keyword.doc)
        assert_equals(keyword_json[-3][0], _StatusHandler._statuses[keyword.status])
        assert_equals(keyword_json[-3][1], self._millis(keyword.starttime))
        self._verify_elapsed(keyword_json[-3][2], keyword)
        for index, message in enumerate(keyword.messages):
            self._verify_message(keyword_json[-1][index], message)
        self._for_each_verify(keyword_json[-2], keyword.keywords, self._verify_keyword)

    def _millis(self, timestamp):
        return self._context.timestamp(timestamp)

    def _assert_html_text(self, text_index, text):
        self._assert_text(text_index, utils.html_escape(text))

    def test_testcase_jsoning(self):
        self._context.start_suite()
        test = TestCase(name='Foo Bar', doc='Test <p>case</p> doc', tags=['foo', 'bar'],
                        timeout='35 years',
                        status='FAIL',
                        message='iz failz!',
                        starttime='20000101 01:00:00.000',
                        endtime='20350101 01:00:00.001')
        parent = lambda:0
        parent.criticality = parent
        parent.test_is_critical = lambda *args: True
        test.parent = parent
        test.keywords.create(name=':FOR ${i} IN RANGE 123', type='for',
                             status='FAIL',
                             starttime='20000101 01:00:01.001',
                             endtime='20350101 01:00:00.001').\
                        keywords.create(type='foritem', status='FAIL',
                                        starttime='20000101 01:00:00.999',
                                        endtime='20350101 01:00:00.001').\
                        keywords.create(type='kw', name='Sleep forever',
                                        status='FAIL',
                                        starttime='20000101 01:00:01.000',
                                        endtime='20350101 01:00:00.001')
        test.visit(self._visitor)
        self._verify_test(self.datamodel[0], test)

    def _verify_test(self, test_json, test):
        self._assert_texts(test_json, {0:test.name,
                                       1:test.timeout})
        self._assert_html_text(test_json[3], test.doc)
        assert_equals(test_json[2], int(test.critical == 'yes'))
        self._verify_tags(test_json[4], test.tags)
        self._assert_text(test_json[5][0], _StatusHandler._statuses[test.status])
        assert_equals(test_json[5][1], self._millis(test.starttime))
        self._verify_elapsed(test_json[5][2], test)
        if test.message != '':
            self._assert_text(test_json[5][3], test.message)
        self._for_each_verify(test_json[6], test.keywords, self._verify_keyword)

    def _assert_texts(self, datamodel, index_to_text):
        for index in index_to_text:
            self._assert_text(datamodel[index], index_to_text[index])

    def _verify_tags(self, tags_json, tags):
        assert_equals(len(tags_json), len(tags))
        for tag_json, tag in zip(tags_json, tags):
            self._assert_text(tag_json, tag)

    def test_suite_jsoning(self):
        suite = TestSuite(source='../somewhere',
                          name='Somewhere',
                          doc='suite <b>documentation</b>',
                          metadata={'key<':'value<!>',
                                    'key2>':'va>lue2'})
        suite.starttime = '20000101 02:23:01.821'
        suite.endtime   = '20011221 11:31:12.371'
        suite.message   = 'so long and thank you for all the fish!'
        suite.keywords.create(type='setup')
        subsuite = suite.suites.create(name='subsuite')
        subsuite.tests.create(name='test', status='PASS')
        suite.keywords.create(type='teardown')
        suite.visit(self._visitor)
        self._verify_suite(self.datamodel[0], suite)

    def _verify_suite(self, suite_json, suite):
        self._assert_text(suite_json[0], suite.name)
        self._assert_text(suite_json[1], suite.source)
        self._assert_text(suite_json[2], '')
        self._assert_html_text(suite_json[3], suite.doc)
        self._verify_metadata(suite_json[4], suite.metadata)
        assert_equals(suite_json[5][0], _StatusHandler._statuses[suite.status])
        assert_equals(suite_json[5][1], self._millis(suite.starttime))
        self._verify_elapsed(suite_json[5][2], suite)
        if suite.message != '':
            self._assert_text(suite_json[5][3], suite.message)
        self._for_each_verify(suite_json[6], suite.suites, self._verify_suite)
        self._for_each_verify(suite_json[7], suite.tests, self._verify_test)
        self._for_each_verify(suite_json[8], suite.keywords, self._verify_keyword)

    def _for_each_verify(self, json, item_list, method):
        for index, subitem in enumerate(item_list):
            method(json[index], subitem)
        assert_equals(len(json), len(item_list))

    def _verify_elapsed(self, elapsed, item):
        if item.starttime != 'N/A':
            assert_equals(elapsed, self._millis(item.endtime)-self._millis(item.starttime))
        else:
            assert_equals(elapsed, 0)

    def _verify_metadata(self, metadata_json, metadata):
        expected = []
        for k,v in metadata.items():
            expected += [k,utils.html_escape(v)]
        for index, value in enumerate(expected):
            self._assert_text(metadata_json[index], value)

    def test_execution_result_jsoning(self):
        result = ExecutionResult()
        result.suite.source = 'kekkonen.html'
        result.suite.name = 'Kekkonen'
        result.suite.doc = 'Foo<h1>Bar</h1>'
        result.generator = 'unit test'
        result.suite.suites.create(name='Urho').tests.create(status='FAIL', name='moi', tags=['tagi']).keywords.create(name='FAILING', status='FAIL').messages.create(message='FAIL', level='WARN', timestamp='20110101 01:01:01.111')
        result.errors.messages.create(message='FAIL', level='WARN', timestamp='20110101 01:01:01.111', linkable=True)
        self._visitor = DatamodelVisitor(result)
        self._context = self._visitor._context
        result.visit(self._visitor)
        self._verify_message(self.datamodel['errors'][0], result.errors.messages[0])
        assert_equals(self._context.dump_texts()[self.datamodel['errors'][0][3]], '*s1-s1-t1-k1')
        self._verify_suite(self.datamodel['suite'], result.suite)
        assert_equals(self.datamodel['generator'], result.generator)
        assert_equals(self.datamodel['baseMillis'], self._context.basemillis)
        assert_equals(len(self.datamodel['strings']), 10)
        assert_equals(self.datamodel['stats'],
            [[{'fail': 1, 'label': 'Critical Tests', 'pass': 0},
              {'fail': 1, 'label': 'All Tests', 'pass': 0}],
             [{'fail': 1, 'label': 'tagi', 'pass': 0}],
             [{'fail': 1, 'label': 'Kekkonen', 'id': 's1', 'name': 'Kekkonen', 'pass': 0},
              {'fail': 1, 'label': 'Kekkonen.Urho', 'id': 's1-s1', 'name': 'Urho', 'pass': 0}]])


if __name__ == '__main__':
    unittest.main()
