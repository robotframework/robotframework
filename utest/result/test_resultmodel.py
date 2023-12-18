import json
import os
import sys
import tempfile
import unittest
import warnings
from datetime import datetime, timedelta
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as ET

from jsonschema import Draft202012Validator

from robot.model import Tags, BodyItem
from robot.result import (Break, Continue, Error, ExecutionResult, For, If, IfBranch,
                          Keyword, Message, Return, TestCase, TestSuite, Try, TryBranch,
                          Var, While)
from robot.utils.asserts import (assert_equal, assert_false, assert_raises,
                                 assert_raises_with_msg, assert_true)


CURDIR = Path(__file__).resolve().parent


class TestSuiteStats(unittest.TestCase):

    def test_stats(self):
        suite = self._create_suite_with_tests()
        assert_equal(suite.statistics.passed, 3)
        assert_equal(suite.statistics.failed, 2)
        assert_equal(suite.statistics.skipped, 1)

    def test_nested_suite_stats(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.statistics.passed, 6)
        assert_equal(suite.statistics.failed, 4)
        assert_equal(suite.statistics.skipped, 2)

    def test_test_count(self):
        suite = self._create_nested_suite_with_tests()
        assert_equal(suite.test_count, 12)
        assert_equal(suite.suites[0].test_count, 6)
        suite.suites.append(self._create_suite_with_tests())
        assert_equal(suite.test_count, 18)
        assert_equal(suite.suites[-1].test_count, 6)
        suite.suites[-1].tests.create()
        assert_equal(suite.test_count, 19)
        assert_equal(suite.suites[-1].test_count, 7)

    def _create_nested_suite_with_tests(self):
        suite = TestSuite()
        suite.suites = [self._create_suite_with_tests(),
                        self._create_suite_with_tests()]
        return suite

    def _create_suite_with_tests(self):
        suite = TestSuite()
        suite.tests = [TestCase(status='PASS'),
                       TestCase(status='PASS'),
                       TestCase(status='PASS'),
                       TestCase(status='FAIL'),
                       TestCase(status='FAIL'),
                       TestCase(status='SKIP')]
        return suite


class TestSuiteStatus(unittest.TestCase):

    def test_suite_status_is_skip_if_there_are_no_tests(self):
        assert_equal(TestSuite().status, 'SKIP')

    def test_suite_status_is_fail_if_failed_test(self):
        suite = TestSuite()
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'PASS')
        suite.tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'FAIL')

    def test_suite_status_is_pass_if_only_passed_tests(self):
        suite = TestSuite()
        for i in range(10):
            suite.tests.create(status='PASS')
        assert_equal(suite.status, 'PASS')

    def test_suite_status_is_pass_if_passed_and_skipped(self):
        suite = TestSuite()
        for i in range(5):
            suite.tests.create(status='PASS')
            suite.tests.create(status='SKIP')
        assert_equal(suite.status, 'PASS')

    def test_suite_status_is_skip_if_only_skipped_tests(self):
        suite = TestSuite()
        for i in range(10):
            suite.tests.create(status='SKIP')
        assert_equal(suite.status, 'SKIP')
        assert_true(suite.skipped)

    def test_suite_status_is_fail_if_failed_subsuite(self):
        suite = TestSuite()
        suite.suites.create().tests.create(status='FAIL')
        assert_equal(suite.status, 'FAIL')
        suite.tests.create(status='PASS')
        assert_equal(suite.status, 'FAIL')

    def test_status_propertys(self):
        suite = TestSuite()
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='SKIP')
        assert_false(suite.passed)
        assert_false(suite.failed)
        assert_true(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='PASS')
        assert_true(suite.passed)
        assert_false(suite.failed)
        assert_false(suite.skipped)
        assert_false(suite.not_run)
        suite.tests.create(status='FAIL')
        assert_false(suite.passed)
        assert_true(suite.failed)
        assert_false(suite.skipped)
        assert_false(suite.not_run)

    def test_suite_status_cannot_be_set_directly(self):
        suite = TestSuite()
        for attr in 'status', 'passed', 'failed', 'skipped', 'not_run':
            assert_true(hasattr(suite, attr))
            assert_raises(AttributeError, setattr, suite, attr, True)


class TestTimes(unittest.TestCase):

    def test_suite_elapsed_time_when_start_and_end_given(self):
        suite = TestSuite()
        suite.start_time = '2001-01-01 10:00:00.000'
        suite.end_time = '2001-01-01 10:00:01.234'
        self.assert_elapsed(suite, 1.234)

    def assert_elapsed(self, obj, expected):
        assert_equal(obj.elapsedtime, round(expected * 1000))
        assert_equal(obj.elapsed_time.total_seconds(), expected)

    def test_suite_elapsed_time_is_zero_by_default(self):
        self.assert_elapsed(TestSuite(), 0)

    def test_suite_elapsed_time_is_got_from_children_if_suite_does_not_have_times(self):
        suite = TestSuite()
        suite.tests.create(start_time='1999-12-12 12:00:00.010',
                           end_time='1999-12-12 12:00:00.011')
        self.assert_elapsed(suite, 0.001)
        suite.start_time = '1999-12-12 12:00:00.010'
        suite.end_time = '1999-12-12 12:00:01.010'
        self.assert_elapsed(suite, 1)

    def test_datetime_and_string(self):
        for cls in (TestSuite, TestCase, Keyword, If, IfBranch, Try, TryBranch,
                    For, While, Break, Continue, Return, Error):
            obj = cls(start_time='2023-05-12T16:40:00.001',
                      end_time='2023-05-12 16:40:01.123456')
            assert_equal(obj.starttime, '20230512 16:40:00.001')
            assert_equal(obj.endtime, '20230512 16:40:01.123')
            assert_equal(obj.start_time, datetime(2023, 5, 12, 16, 40, 0, 1000))
            assert_equal(obj.end_time, datetime(2023, 5, 12, 16, 40, 1, 123456))
            self.assert_elapsed(obj, 1.122456)
            obj.config(start_time='2023-09-07 20:33:44.444444',
                       end_time=datetime(2023, 9, 7, 20, 33, 44, 999999))
            assert_equal(obj.starttime, '20230907 20:33:44.444')
            assert_equal(obj.endtime, '20230907 20:33:44.999')
            assert_equal(obj.start_time, datetime(2023, 9, 7, 20, 33, 44, 444444))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 20, 33, 44, 999999))
            self.assert_elapsed(obj, 0.555555)
            obj.config(starttime='20230907 20:33:44.555555',
                       endtime='20230907 20:33:44.999999')
            assert_equal(obj.starttime, '20230907 20:33:44.555')
            assert_equal(obj.endtime, '20230907 20:33:44.999')
            assert_equal(obj.start_time, datetime(2023, 9, 7, 20, 33, 44, 555555))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 20, 33, 44, 999999))
            self.assert_elapsed(obj, 0.444444)

    def test_times_are_calculated_if_not_set(self):
        for cls in (TestSuite, TestCase, Keyword, If, IfBranch, Try, TryBranch,
                    For, While, Break, Continue, Return, Error):
            obj = cls()
            assert_equal(obj.start_time, None)
            assert_equal(obj.end_time, None)
            assert_equal(obj.elapsed_time, timedelta())
            obj.config(start_time='2023-09-07 12:34:56',
                       end_time='2023-09-07T12:34:57',
                       elapsed_time=42)
            assert_equal(obj.start_time, datetime(2023, 9, 7, 12, 34, 56))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 12, 34, 57))
            assert_equal(obj.elapsed_time, timedelta(seconds=42))
            obj.config(elapsed_time=None)
            assert_equal(obj.start_time, datetime(2023, 9, 7, 12, 34, 56))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 12, 34, 57))
            assert_equal(obj.elapsed_time, timedelta(seconds=1))
            obj.config(elapsed_time=0)
            assert_equal(obj.start_time, datetime(2023, 9, 7, 12, 34, 56))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 12, 34, 57))
            assert_equal(obj.elapsed_time, timedelta(seconds=0))
            obj.config(end_time=None,
                       elapsed_time=timedelta(seconds=2))
            assert_equal(obj.start_time, datetime(2023, 9, 7, 12, 34, 56))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 12, 34, 58))
            assert_equal(obj.elapsed_time, timedelta(seconds=2))
            obj.config(start_time=None,
                       end_time=obj.start_time,
                       elapsed_time=timedelta(seconds=10))
            assert_equal(obj.start_time, datetime(2023, 9, 7, 12, 34, 46))
            assert_equal(obj.end_time, datetime(2023, 9, 7, 12, 34, 56))
            assert_equal(obj.elapsed_time, timedelta(seconds=10))
            obj.config(start_time=None,
                       end_time=None)
            assert_equal(obj.start_time, None)
            assert_equal(obj.end_time, None)
            assert_equal(obj.elapsed_time, timedelta(seconds=10))

    def test_suite_elapsed_time(self):
        suite = TestSuite()
        suite.tests.create(elapsed_time=1)
        suite.suites.create(elapsed_time=2)
        assert_equal(suite.elapsed_time, timedelta(seconds=3))
        suite.setup.config(name='S', elapsed_time=0.1)
        suite.teardown.config(name='T', elapsed_time=0.2)
        assert_equal(suite.elapsed_time, timedelta(seconds=3.3))
        suite.config(start_time=datetime(2023, 9, 7, 20, 33, 44),
                     end_time=datetime(2023, 9, 7, 20, 33, 45),)
        assert_equal(suite.elapsed_time, timedelta(seconds=1))
        suite.elapsed_time = 42
        assert_equal(suite.elapsed_time, timedelta(seconds=42))

    def test_test_elapsed_time(self):
        test = TestCase()
        test.body.create_keyword(elapsed_time=1)
        test.body.create_if(elapsed_time=2)
        assert_equal(test.elapsed_time, timedelta(seconds=3))
        test.setup.config(name='S', elapsed_time=0.1)
        test.teardown.config(name='T', elapsed_time=0.2)
        assert_equal(test.elapsed_time, timedelta(seconds=3.3))
        test.config(start_time=datetime(2023, 9, 7, 20, 33, 44),
                    end_time=datetime(2023, 9, 7, 20, 33, 45),)
        assert_equal(test.elapsed_time, timedelta(seconds=1))
        test.elapsed_time = 42
        assert_equal(test.elapsed_time, timedelta(seconds=42))

    def test_keyword_elapsed_time(self):
        kw = Keyword()
        kw.body.create_keyword(elapsed_time=1)
        kw.body.create_if(elapsed_time=2)
        assert_equal(kw.elapsed_time, timedelta(seconds=3))
        kw.teardown.config(name='T', elapsed_time=0.2)
        assert_equal(kw.elapsed_time, timedelta(seconds=3.2))
        kw.config(start_time=datetime(2023, 9, 7, 20, 33, 44),
                  end_time=datetime(2023, 9, 7, 20, 33, 45),)
        assert_equal(kw.elapsed_time, timedelta(seconds=1))
        kw.elapsed_time = 42
        assert_equal(kw.elapsed_time, timedelta(seconds=42))

    def test_control_structure_elapsed_time(self):
        for cls in (If, IfBranch, Try, TryBranch, For, While, Break, Continue,
                    Return, Error):
            obj = cls()
            obj.body.create_keyword(elapsed_time=1)
            obj.body.create_keyword(elapsed_time=2)
            assert_equal(obj.elapsed_time, timedelta(seconds=3))
            obj.config(start_time=datetime(2023, 9, 7, 20, 33, 44),
                       end_time=datetime(2023, 9, 7, 20, 33, 45),)
            assert_equal(obj.elapsed_time, timedelta(seconds=1))
            obj.elapsed_time = 42
            assert_equal(obj.elapsed_time, timedelta(seconds=42))


class TestSlots(unittest.TestCase):

    def test_testsuite(self):
        self._verify(TestSuite())

    def test_testcase(self):
        self._verify(TestCase())

    def test_keyword(self):
        self._verify(Keyword())

    def test_if(self):
        self._verify(If())
        self._verify(If().body.create_branch())

    def test_for(self):
        self._verify(For())
        self._verify(For().body.create_iteration())

    def test_try(self):
        self._verify(Try())
        self._verify(Try().body.create_branch())

    def test_while(self):
        self._verify(While())
        self._verify(While().body.create_iteration())

    def test_break_continue_return(self):
        for cls in Break, Continue, Return:
            self._verify(cls())

    def test_error(self):
        self._verify(Error())

    def test_message(self):
        self._verify(Message())

    def _verify(self, item):
        assert_raises(AttributeError, setattr, item, 'attr', 'value')


class TestModel(unittest.TestCase):

    def test_keyword_name(self):
        kw = Keyword('keyword')
        assert_equal(kw.name, 'keyword')
        assert_equal(kw.owner, None)
        assert_equal(kw.full_name, 'keyword')
        assert_equal(kw.source_name, None)
        kw = Keyword('keyword', 'library', 'key${x}')
        assert_equal(kw.name, 'keyword')
        assert_equal(kw.owner, 'library')
        assert_equal(kw.full_name, 'library.keyword')
        assert_equal(kw.source_name, 'key${x}')

    def test_full_name_cannot_be_set_directly(self):
        assert_raises(AttributeError, setattr, Keyword(), 'full_name', 'value')

    def test_deprecated_names(self):
        # These aren't loudly deprecated yet.
        kw = Keyword('k', 'l', 's')
        assert_equal(kw.kwname, 'k')
        assert_equal(kw.libname, 'l')
        assert_equal(kw.sourcename, 's')
        kw.kwname, kw.libname, kw.sourcename = 'K', 'L', 'S'
        assert_equal(kw.kwname, 'K')
        assert_equal(kw.libname, 'L')
        assert_equal(kw.sourcename, 'S')
        assert_equal(kw.name, 'K')
        assert_equal(kw.owner, 'L')
        assert_equal(kw.source_name, 'S')
        assert_equal(kw.full_name, 'L.K')

    def test_status_propertys_with_test(self):
        self._verify_status_propertys(TestCase())

    def test_status_propertys_with_keyword(self):
        self._verify_status_propertys(Keyword())

    def test_status_propertys_with_control_structures(self):
        for obj in (Break(), Continue(), Return(), Error(),
                    For(), For().body.create_iteration(),
                    If(), If().body.create_branch(),
                    Try(), Try().body.create_branch(),
                    While(), While().body.create_iteration()):
            self._verify_status_propertys(obj)

    def test_keyword_passed_after_dry_run(self):
        self._verify_status_propertys(Keyword(status=Keyword.NOT_RUN),
                                      initial_status=Keyword.NOT_RUN)

    def _verify_status_propertys(self, item, initial_status='FAIL'):
        item.starttime = '20210121 17:04:00.000'
        item.endtime = '20210121 17:04:01.002'
        assert_equal(item.elapsedtime, 1002)
        assert_equal(item.passed, initial_status == item.PASS)
        assert_equal(item.failed, initial_status == item.FAIL)
        assert_equal(item.skipped, initial_status == item.SKIP)
        assert_equal(item.not_run, initial_status == item.NOT_RUN)
        assert_equal(item.status, initial_status)
        item.passed = True
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'PASS')
        item.passed = False
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'FAIL')
        item.failed = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, True)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'FAIL')
        item.failed = False
        assert_equal(item.passed, True)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, False)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'PASS')
        item.skipped = True
        assert_equal(item.passed, False)
        assert_equal(item.failed, False)
        assert_equal(item.skipped, True)
        assert_equal(item.not_run, False)
        assert_equal(item.status, 'SKIP')
        assert_raises(ValueError, setattr, item, 'skipped', False)
        if isinstance(item, TestCase):
            assert_raises(AttributeError, setattr, item, 'not_run', True)
            assert_raises(AttributeError, setattr, item, 'not_run', False)
        else:
            item.not_run = True
            assert_equal(item.passed, False)
            assert_equal(item.failed, False)
            assert_equal(item.skipped, False)
            assert_equal(item.not_run, True)
            assert_equal(item.status, 'NOT RUN')
            assert_raises(ValueError, setattr, item, 'not_run', False)

    def test_keyword_teardown(self):
        kw = Keyword()
        assert_true(not kw.has_teardown)
        assert_true(not kw.teardown)
        assert_equal(kw.teardown.name, None)
        assert_equal(kw.teardown.type, 'TEARDOWN')
        assert_true(not kw.has_teardown)
        assert_true(not kw.teardown)
        kw.teardown = Keyword()
        assert_true(kw.has_teardown)
        assert_true(kw.teardown)
        assert_equal(kw.teardown.name, '')
        assert_equal(kw.teardown.type, 'TEARDOWN')
        kw.teardown = None
        assert_true(not kw.has_teardown)
        assert_true(not kw.teardown)
        assert_equal(kw.teardown.name, None)
        assert_equal(kw.teardown.type, 'TEARDOWN')

    def test_for_parents(self):
        test = TestCase()
        for_ = test.body.create_for()
        assert_equal(for_.parent, test)
        iter1 = for_.body.create_iteration()
        assert_equal(iter1.parent, for_)
        kw = iter1.body.create_keyword()
        assert_equal(kw.parent, iter1)
        iter2 = for_.body.create_iteration()
        assert_equal(iter2.parent, for_)
        kw = iter2.body.create_keyword()
        assert_equal(kw.parent, iter2)

    def test_if_parents(self):
        test = TestCase()
        if_ = test.body.create_if()
        assert_equal(if_.parent, test)
        branch = if_.body.create_branch(if_.IF, '$x > 0')
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)
        branch = if_.body.create_branch(if_.ELSE_IF, '$x < 0')
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)
        branch = if_.body.create_branch(if_.ELSE)
        assert_equal(branch.parent, if_)
        kw = branch.body.create_keyword()
        assert_equal(kw.parent, branch)

    def test_while_log_name(self):
        assert_equal(While()._log_name, '')
        assert_equal(While('$x > 0')._log_name, '$x > 0')
        assert_equal(While('True', '1 minute')._log_name,
                     'True    limit=1 minute')
        assert_equal(While(limit='1 minute')._log_name,
                     'limit=1 minute')
        assert_equal(While('True', '1 s', on_limit_message='x')._log_name,
                     'True    limit=1 s    on_limit_message=x')
        assert_equal(While(on_limit='pass', limit='100')._log_name,
                     'limit=100    on_limit=pass')
        assert_equal(While(on_limit_message='Error message')._log_name,
                     'on_limit_message=Error message')

    def test_for_log_name(self):
        assert_equal(For(assign=['${x}'], values=['a', 'b'])._log_name,
                     '${x}    IN    a    b')
        assert_equal(For(['${x}'], 'IN ENUMERATE', ['a', 'b'], start='1')._log_name,
                     '${x}    IN ENUMERATE    a    b    start=1')
        assert_equal(For(['${x}', '${y}'], 'IN ZIP', ['${xs}', '${ys}'],
                         mode='STRICT', fill='-')._log_name,
                     '${x}    ${y}    IN ZIP    ${xs}    ${ys}    mode=STRICT    fill=-')

    def test_try_log_name(self):
        for typ in TryBranch.TRY, TryBranch.EXCEPT, TryBranch.ELSE, TryBranch.FINALLY:
            assert_equal(TryBranch(typ)._log_name, '')
        branch = TryBranch(TryBranch.EXCEPT)
        assert_equal(branch.config(patterns=['p1', 'p2'])._log_name,
                     'p1    p2')
        assert_equal(branch.config(pattern_type='glob')._log_name,
                     'p1    p2    type=glob')
        assert_equal(branch.config(assign='${err}')._log_name,
                     'p1    p2    type=glob    AS    ${err}')

    def test_var_log_name(self):
        assert_equal(Var('${x}', 'y')._log_name,
                     '${x}    y')
        assert_equal(Var('${x}', ('y', 'z'))._log_name,
                     '${x}    y    z')
        assert_equal(Var('${x}', ('y', 'z'), separator='')._log_name,
                     '${x}    y    z    separator=')
        assert_equal(Var('@{x}', ('y',), scope='test')._log_name,
                     '@{x}    y    scope=test')


class TestBody(unittest.TestCase):

    def test_only_keywords(self):
        kw = Keyword()
        for i in range(10):
            kw.body.create_keyword(str(i))
        assert_equal([k.name for k in kw.body], [str(i) for i in range(10)])

    def test_only_messages(self):
        kw = Keyword()
        for i in range(10):
            kw.body.create_message(str(i))
        assert_equal([m.message for m in kw.body], [str(i) for i in range(10)])

    def test_order(self):
        kw = Keyword()
        m1 = kw.body.create_message('m1')
        k1 = kw.body.create_keyword('k1')
        k2 = kw.body.create_keyword('k2')
        m2 = kw.body.create_message('m2')
        k3 = kw.body.create_keyword('k3')
        assert_equal(list(kw.body), [m1, k1, k2, m2, k3])

    def test_order_after_modifications(self):
        kw = Keyword('parent')
        kw.body.create_keyword('k1')
        kw.body.create_message('m1')
        k2 = kw.body.create_keyword('k2')
        m2 = kw.body.create_message('m2')
        k1 = kw.body[0] = Keyword('k1-new')
        m1 = kw.body[1] = Message('m1-new')
        m3 = Message('m3')
        kw.body.append(m3)
        k3 = Keyword('k3')
        kw.body.extend([k3])
        assert_equal(list(kw.body), [k1, m1, k2, m2, m3, k3])
        kw.body = [k3, m2, k1]
        assert_equal(list(kw.body), [k3, m2, k1])

    def test_id(self):
        kw = TestSuite().tests.create().body.create_keyword()
        kw.body = [Keyword(), Message(), Keyword()]
        kw.body[-1].body = [Message(), Keyword(), Message()]
        assert_equal(kw.body[0].id, 's1-t1-k1-k1')
        assert_equal(kw.body[1].id, 's1-t1-k1-m1')
        assert_equal(kw.body[2].id, 's1-t1-k1-k2')
        assert_equal(kw.body[2].body[0].id, 's1-t1-k1-k2-m1')
        assert_equal(kw.body[2].body[1].id, 's1-t1-k1-k2-k1')
        assert_equal(kw.body[2].body[2].id, 's1-t1-k1-k2-m2')


class TestIterations(unittest.TestCase):

    def test_create_supported(self):
        for parent in For(), While():
            iterations = parent.body
            for creator in (iterations.create_iteration,
                            iterations.create_message,
                            iterations.create_keyword):
                item = creator()
                assert_equal(item.parent, parent)

    def test_create_not_supported(self):
        msg = "'robot.result.Iterations' object does not support '{}'."
        for parent in For(), While():
            iterations = parent.body
            for creator in (iterations.create_for,
                            iterations.create_if,
                            iterations.create_try,
                            iterations.create_return):
                assert_raises_with_msg(TypeError, msg.format(creator.__name__), creator)


class TestBranches(unittest.TestCase):

    def test_create_supported(self):
        for parent in If(), Try():
            branches = parent.body
            for creator in (branches.create_branch,
                            branches.create_message,
                            branches.create_keyword):
                item = creator()
                assert_equal(item.parent, parent)

    def test_create_not_supported(self):
        msg = "'robot.result.Branches' object does not support '{}'."
        for parent in If(), Try():
            branches = parent.body
            for creator in (branches.create_for,
                            branches.create_if,
                            branches.create_try,
                            branches.create_return):
                assert_raises_with_msg(TypeError, msg.format(creator.__name__), creator)


class TestToFromDictAndJson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open(CURDIR / '../../doc/schema/result.json') as file:
            schema = json.load(file)
        cls.validator = Draft202012Validator(schema=schema)
        cls.maxDiff = 2000

    def test_keyword(self):
        self._verify(Keyword(), name='', status='FAIL', elapsed_time=0)
        self._verify(Keyword('Name'), name='Name', status='FAIL', elapsed_time=0)
        now = datetime.now()
        keyword = Keyword('N', 'BuiltIn', 'N', 'some doc', ('args',),
                          ('${result}',), ('t1', 't2'), "1s",
                          BodyItem.KEYWORD, "PASS", 'a msg', now, None, 1.2)
        keyword.setup.config(name='Setup', status='PASS')
        keyword.teardown.config(name='Teardown', args='a')
        keyword.body.create_keyword("K1", status='PASS')
        self._verify(
            keyword,
            name='N',
            status='PASS',
            owner='BuiltIn',
            source_name='N',
            doc='some doc',
            args=('args', ),
            assign=('${result}',),
            tags=['t1', 't2'],
            timeout="1s",
            message='a msg',
            start_time=now.isoformat(),
            elapsed_time=1.2,
            setup={'name': 'Setup', 'status': 'PASS', 'elapsed_time': 0},
            teardown={'name': 'Teardown', 'status': 'FAIL', 'args': ('a', ), 'elapsed_time': 0},
            body=[{'name': 'K1', 'status': 'PASS', 'elapsed_time': 0}]
        )

    def test_for(self):
        self._verify(For(), type='FOR', assign=(), flavor='IN', values=(), body=[], status='FAIL', elapsed_time=0)
        self._verify(For(['${i}'], 'IN RANGE', ['10']),
                     type='FOR', assign=('${i}',), flavor='IN RANGE', values=('10',),
                     body=[], status='FAIL', elapsed_time=0)
        root = For(['${i}', '${a}'], 'IN ENUMERATE', ['cat', 'dog'], start='1')
        iter_ = root.body.create_iteration({"${x}": "1"})
        iter_.body.create_keyword('K1')
        self._verify(root,
                     type='FOR', assign=('${i}', '${a}'), flavor='IN ENUMERATE',
                     values=('cat', 'dog'), start='1', status='FAIL', elapsed_time=0,
                     body=[{'type': 'ITERATION', 'assign': {'${x}': '1'}, 'status': 'FAIL', 'elapsed_time': 0,
                            'body': [{'name': 'K1', 'status': 'FAIL', 'elapsed_time': 0}]}])

    def test_while(self):
        self._verify(While(limit='1', on_limit_message='Ooops!', status='PASS'),
                     type='WHILE', limit='1', on_limit_message='Ooops!', status='PASS', elapsed_time=0, body=[])
        root = While('True')
        iter_ = root.body.create_iteration()
        iter_.body.create_keyword('K')
        self._verify(root, type='WHILE', condition='True', status='FAIL', elapsed_time=0,
                     body=[{'type': 'ITERATION', 'status': 'FAIL', 'elapsed_time': 0,
                           'body': [{'name': 'K', 'status': 'FAIL', 'elapsed_time': 0}]}
                           ])

    def test_if(self):
        now = datetime.now()
        if_ = If('FAIL', 'I failed', start_time=now, elapsed_time=0.1)
        if_.body.create_branch(condition='0 > 1', status='FAIL', message='I failed', start_time=now, elapsed_time=0.01)
        exp_branch = {
            'condition': '0 > 1',
            'elapsed_time': 0.01,
            'message': 'I failed',
            'start_time': now.isoformat(),
            'status': 'FAIL',
            'type': BodyItem.IF,
            'body': []
        }
        self._verify(if_, type=BodyItem.IF_ELSE_ROOT, status="FAIL", message="I failed", start_time=now.isoformat(),
                     elapsed_time=0.1, body=[exp_branch])

    def test_try_structure(self):
        root = Try()
        root.body.create_branch(Try.TRY).body.create_keyword('K1')
        root.body.create_branch(Try.EXCEPT).body.create_keyword('K2')
        root.body.create_branch(Try.ELSE).body.create_keyword('K3')
        root.body.create_branch(Try.FINALLY).body.create_keyword('K4')
        self._verify(root,
                     status='FAIL',
                     elapsed_time=0,
                     type='TRY/EXCEPT ROOT',
                     body=[{'type': 'TRY', 'status': 'FAIL', 'elapsed_time': 0,
                            'body': [{'name': 'K1', 'status': 'FAIL', 'elapsed_time': 0}]},
                           {'type': 'EXCEPT', 'patterns': (), 'status': 'FAIL', 'elapsed_time': 0,
                            'body': [{'name': 'K2', 'status': 'FAIL', 'elapsed_time': 0}]},
                           {'type': 'ELSE', 'status': 'FAIL', 'elapsed_time': 0,
                            'body': [{'name': 'K3', 'status': 'FAIL', 'elapsed_time': 0}]},
                           {'type': 'FINALLY', 'status': 'FAIL', 'elapsed_time': 0,
                            'body': [{'name': 'K4', 'status': 'FAIL', 'elapsed_time': 0}]}])

    def test_return_continue_break(self):
        self._verify(Return(('x', 'y')),
                     type='RETURN', values=('x', 'y'), status='FAIL', elapsed_time=0)
        self._verify(Continue(), type='CONTINUE', status='FAIL', elapsed_time=0)
        self._verify(Break(), type='BREAK', status='FAIL', elapsed_time=0)
        ret = Return()
        ret.body.create_message('something', 'WARN', True)
        self._verify(ret, type='RETURN', status='FAIL', elapsed_time=0,
                     body=[{'message': 'something', 'level': 'WARN', 'html': True,
                            'type': BodyItem.MESSAGE}])

    def test_message(self):
        now = datetime.now()
        self._verify(Message('a msg', 'DEBUG', False, now),
                     type=BodyItem.MESSAGE, message='a msg', level='DEBUG', html=False,
                     timestamp=now.isoformat())

    def test_test(self):
        self._verify(TestCase(), name='', status='FAIL', body=[], elapsed_time=0)

    def test_testcase_structure(self):
        test = TestCase('TC', 'my doc', ['T1', 'T2'], '1 minute', 42)
        test.setup.config(name='Setup', status='PASS')
        test.teardown.config(name='Teardown', args='a')
        test.body.create_keyword('K1', 'suite')
        test.body.create_if(status='PASS').\
            body.create_branch(condition='$c', status='PASS').\
            body.create_keyword('K2', status='PASS')
        self._verify(test,
                     name='TC',
                     status='FAIL',
                     doc='my doc',
                     tags=('T1', 'T2'),
                     timeout='1 minute',
                     lineno=42,
                     elapsed_time=0,
                     setup={'name': 'Setup', 'status': 'PASS', 'elapsed_time': 0},
                     teardown={'name': 'Teardown', 'status': 'FAIL', 'args': ('a', ),
                               'elapsed_time': 0},
                     body=[{'name': 'K1', 'owner': 'suite', 'status': 'FAIL',
                            'elapsed_time': 0},
                           {'type': 'IF/ELSE ROOT', 'status': 'PASS', 'elapsed_time': 0,
                            'body': [{'type': 'IF', 'condition': '$c', 'status': 'PASS', 'elapsed_time': 0,
                                      'body': [{'name': 'K2', 'status': 'PASS', 'elapsed_time': 0}]
                                      }]}
                           ])

    def test_suite_structure(self):
        suite = TestSuite('Root')
        suite.setup.config(name='Setup', status='PASS')
        suite.teardown.config(name='Teardown', args='a', status='PASS')
        suite.tests.create('T1', status='PASS').body.create_keyword('K', status='PASS')
        suite.suites.create('Child').tests.create('T2')
        self._verify(suite,
                     status='FAIL',
                     name='Root',
                     elapsed_time=0,
                     setup={'name': 'Setup', 'status': 'PASS', 'elapsed_time': 0},
                     teardown={'name': 'Teardown', 'args': ('a',), 'status': 'PASS',
                               'elapsed_time': 0},
                     tests=[{'name': 'T1', 'status': 'PASS', 'elapsed_time': 0,
                             'body': [{'name': 'K', 'status': 'PASS', 'elapsed_time': 0}]}],
                     suites=[{'name': 'Child', 'status': 'FAIL', 'elapsed_time': 0,
                              'tests': [{'name': 'T2', 'status': 'FAIL', 'elapsed_time': 0, 'body': []}]
                            }],
                     )

    def _verify(self, obj, **expected):
        data = obj.to_dict()
        self.assertListEqual(sorted(list(data)), sorted(list(expected)))
        self.assertDictEqual(data, expected)
        roundtrip = type(obj).from_dict(data).to_dict()
        self.assertDictEqual(roundtrip, expected)
        roundtrip = type(obj).from_json(obj.to_json()).to_dict()
        self.assertDictEqual(roundtrip, expected)
        self._validate(obj)

    def _validate(self, obj):
        suite = self._create_suite_structure(obj)
        self.validator.validate(instance=json.loads(suite.to_json()))
        # Validating `suite.to_dict` directly doesn't work due to tuples not
        # being accepted as arrays:
        # https://github.com/python-jsonschema/jsonschema/issues/148
        #self.validator.validate(instance=suite.to_dict())

    def _create_suite_structure(self, obj):
        suite = TestSuite()
        test = suite.tests.create()
        if isinstance(obj, TestSuite):
            suite = obj
        elif isinstance(obj, TestCase):
            suite.tests = [obj]
        elif isinstance(obj, (Keyword, For, While, If, Try, Var, Error, Message)):
            test.body.append(obj)
        elif isinstance(obj, (IfBranch, TryBranch)):
            item = If() if isinstance(obj, IfBranch) else Try()
            item.body.append(obj)
            test.body.append(item)
        elif isinstance(obj, (Break, Continue, Return)):
            branch = test.body.create_if().body.create_branch()
            branch.body.append(obj)
        else:
            raise ValueError(obj)
        return suite


class TestDeprecatedKeywordSpecificAttributes(unittest.TestCase):

    def test_for(self):
        obj = For(['${x}', '${y}'], 'IN', ['a', 'b', 'c', 'd'])
        for attr, expected in [('name', '${x}    ${y}    IN    a    b    c    d'),
                               ('kwname', '${x}    ${y}    IN    a    b    c    d'),
                               ('libname', None),
                               ('args', ()),
                               ('doc', ''),
                               ('tags', Tags()),
                               ('timeout', None)]:
            self._verify_deprecation(obj, attr, expected)

    def test_those_having_assign(self):
        for obj in For().body.create_iteration(), Try().body.create_branch():
            for attr, expected in [('name', ''),
                                   ('kwname', ''),
                                   ('libname', None),
                                   ('args', ()),
                                   ('doc', ''),
                                   ('tags', Tags()),
                                   ('timeout', None)]:
                self._verify_deprecation(obj, attr, expected)

    def test_others(self):
        for obj in (If(), If().body.create_branch(), Try(),
                    While(), While().body.create_iteration(),
                    Break(), Continue(), Return(), Error()):
            for attr, expected in [('name', ''),
                                   ('kwname', ''),
                                   ('libname', None),
                                   ('args', ()),
                                   ('doc', ''),
                                   ('assign', ()),
                                   ('tags', Tags()),
                                   ('timeout', None)]:
                self._verify_deprecation(obj, attr, expected)

    def _verify_deprecation(self, obj, attr, expected):
        name = type(obj).__name__
        with warnings.catch_warnings(record=True) as w:
            assert_equal(getattr(obj, attr), expected, f'{name}.{attr}')
            assert_true(issubclass(w[-1].category, UserWarning))
            assert_equal(str(w[-1].message),
                         f"'robot.result.{name}.{attr}' is deprecated and "
                         f"will be removed in Robot Framework 8.0.")


class TestSuiteToFromXml(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        golden = CURDIR / 'golden.xml'
        cls.suite = ExecutionResult(golden).suite
        cls.xml = ET.tostring(ET.parse(golden).find('suite'), encoding='unicode')

    def test_to_string(self):
        self._verify_xml(self.suite.to_xml())

    def test_from_string(self):
        self._verify_suite(TestSuite.from_xml(self.xml))

    def test_to_file(self):
        file = StringIO()
        assert self.suite.to_xml(file) is None
        self._verify_xml(file.getvalue())
        assert not file.closed

    def test_from_file(self):
        file = StringIO(self.xml)
        self._verify_suite(TestSuite.from_xml(file))
        assert not file.closed

    def test_to_path(self):
        path = Path(os.getenv('TEMPDIR', tempfile.gettempdir()), 'suite.xml')
        assert self.suite.to_xml(path) is None
        self._verify_suite(TestSuite.from_xml(path))
        self.suite.to_xml(str(path))
        self._verify_suite(TestSuite.from_xml(path))

    def test_from_path(self):
        self._verify_suite(TestSuite.from_xml(CURDIR / 'golden.xml'))
        self._verify_suite(TestSuite.from_xml(str(CURDIR / 'golden.xml')))

    def _verify_suite(self, suite):
        self._verify_xml(suite.to_xml())

    def _verify_xml(self, xml):
        kws = {'strict': True} if sys.version_info >= (3, 10) else {}
        for exp, act in zip(self.xml.splitlines(), xml.splitlines(), **kws):
            assert_equal(exp.replace(' />', '/>'), act)


if __name__ == '__main__':
    unittest.main()
