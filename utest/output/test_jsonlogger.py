import unittest
from fnmatch import fnmatchcase
from io import StringIO
from typing import cast

from robot.output.jsonlogger import JsonLogger
from robot.result import *


class TestJsonLogger(unittest.TestCase):
    start = '2024-12-03T12:27:00.123456'

    def setUp(self):
        self.logger = JsonLogger(StringIO())

    def test_start(self):
        self.verify('''{
"generator":"Robot * (* on *)",
"generated":"20??-??-??T??:??:??.??????",
"rpa":false''', glob=True)

    def test_start_suite(self):
        self.test_start()
        self.logger.start_suite(TestSuite())
        self.verify(''',
"suite":{
"id":"s1"''')

    def test_end_suite(self):
        self.test_start_suite()
        self.logger.end_suite(TestSuite())
        self.verify(''',
"status":"SKIP",
"elapsed_time":0.000000
}''')

    def test_suite_with_config(self):
        self.test_start()
        suite = TestSuite(name='Suite', doc='The doc!', metadata={'N': 'V', 'n2': 'v2'},
                          source='tests.robot', rpa=True, start_time=self.start,
                          elapsed_time=3.14, message="Message")
        self.logger.start_suite(suite)
        self.verify(''',
"suite":{
"id":"s1"''')
        self.logger.end_suite(suite)
        self.verify(''',
"name":"Suite",
"doc":"The doc!",
"metadata":{"N":"V","n2":"v2"},
"source":"tests.robot",
"rpa":true,
"status":"SKIP",
"message":"Message",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":3.140000
}''')

    def test_child_suite(self):
        self.test_start_suite()
        suite = TestSuite(name='C', doc='Child', start_time=self.start)
        suite.tests.create(name='T', status='PASS', elapsed_time=1)
        self.logger.start_suite(suite)
        self.verify(''',
"suites":[{
"id":"s1"''')
        self.logger.end_suite(suite)
        self.verify(''',
"name":"C",
"doc":"Child",
"status":"PASS",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":1.000000
}''')

    def test_suite_setup(self):
        self.test_start_suite()
        setup = Keyword(type=Keyword.SETUP, name='S', start_time=self.start)
        self.logger.start_keyword(setup)
        self.verify(''',
"setup":{''')
        self.logger.end_keyword(setup)
        self.verify('''
"name":"S",
"status":"FAIL",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":0.000000
}''')

    def test_suite_teardown(self):
        self.test_suite_setup()
        suite = TestSuite()
        suite.teardown.config(name='T', status='PASS')
        self.logger.start_keyword(suite.teardown)
        self.verify(''',
"teardown":{''')
        self.logger.end_keyword(suite.teardown)
        self.verify('''
"name":"T",
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_suite_teardown_after_suites(self):
        self.test_child_suite()
        suite = TestSuite()
        suite.teardown.config(name='T', status='PASS')
        self.logger.start_keyword(suite.teardown)
        self.verify('''],
"teardown":{''')
        self.logger.end_keyword(suite.teardown)
        self.verify('''
"name":"T",
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_suite_teardown_after_tests(self):
        self.test_end_test()
        suite = TestSuite()
        suite.teardown.config(name='T', doc='suite teardown', status='PASS')
        self.logger.start_keyword(suite.teardown)
        self.verify('''],
"teardown":{''')
        self.logger.end_keyword(suite.teardown)
        self.verify('''
"name":"T",
"doc":"suite teardown",
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_suite_structure(self):
        root = TestSuite()
        self.test_start_suite()
        self.logger.start_suite(root.suites.create(name='Child', doc='child'))
        self.verify(''',
"suites":[{
"id":"s1-s1"''')
        self.logger.start_suite(root.suites[0].suites.create(name='GC', doc='gc'))
        self.verify(''',
"suites":[{
"id":"s1-s1-s1"''')
        self.logger.start_test(root.suites[0].suites[0].tests.create(name='1', doc='1'))
        self.logger.end_test(root.suites[0].suites[0].tests[0])
        self.verify(''',
"tests":[{
"id":"s1-s1-s1-t1",
"name":"1",
"doc":"1",
"status":"FAIL",
"elapsed_time":0.000000
}''')
        self.logger.start_test(root.suites[0].suites[0].tests.create(name='2', doc='2',
                                                                     status='PASS'))
        self.logger.end_test(root.suites[0].suites[0].tests[1])
        self.verify(''',{
"id":"s1-s1-s1-t2",
"name":"2",
"doc":"2",
"status":"PASS",
"elapsed_time":0.000000
}''')
        self.logger.end_suite(root.suites[0].suites[0])
        self.verify('''],
"name":"GC",
"doc":"gc",
"status":"FAIL",
"elapsed_time":0.000000
}''')
        self.logger.start_suite(root.suites[0].suites.create(name='GC2'))
        self.logger.end_suite(root.suites[0].suites[1])
        self.verify(''',{
"id":"s1-s1-s2",
"name":"GC2",
"status":"SKIP",
"elapsed_time":0.000000
}''')
        self.logger.end_suite(root.suites[0])
        self.verify('''],
"name":"Child",
"doc":"child",
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_suite_with_suites_and_tests(self):
        self.test_start_suite()
        root = TestSuite()
        suite1 = root.suites.create('Suite 1')
        suite2 = root.suites.create('Suite 2')
        test1 = root.tests.create('Test 1')
        test2 = root.tests.create('Test 2')
        self.logger.start_suite(suite1)
        self.logger.end_suite(suite1)
        self.logger.start_suite(suite2)
        self.logger.end_suite(suite2)
        self.verify(''',
"suites":[{
"id":"s1-s1",
"name":"Suite 1",
"status":"SKIP",
"elapsed_time":0.000000
},{
"id":"s1-s2",
"name":"Suite 2",
"status":"SKIP",
"elapsed_time":0.000000
}''')
        self.logger.start_test(test1)
        self.logger.end_test(test1)
        self.logger.start_test(test2)
        self.logger.end_test(test2)
        self.verify('''],
"tests":[{
"id":"s1-t1",
"name":"Test 1",
"status":"FAIL",
"elapsed_time":0.000000
},{
"id":"s1-t2",
"name":"Test 2",
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_start_test(self):
        self.test_start_suite()
        self.logger.start_test(TestCase())
        self.verify(''',
"tests":[{
"id":"t1"''')

    def test_end_test(self):
        self.test_start_test()
        self.logger.end_test(TestCase())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_test_with_config(self):
        self.test_start_suite()
        test = TestCase(name='First!', doc='Doc', tags=['t1', 't2'], lineno=42,
                        timeout='1 hour', status='PASS', message='Hello, world!',
                        start_time=self.start, elapsed_time=1)
        self.logger.start_test(test)
        self.verify(''',
"tests":[{
"id":"t1"''')
        self.logger.end_test(test)
        self.verify(''',
"name":"First!",
"doc":"Doc",
"tags":["t1","t2"],
"lineno":42,
"timeout":"1 hour",
"status":"PASS",
"message":"Hello, world!",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":1.000000
}''')

    def test_start_subsequent_test(self):
        self.test_end_test()
        self.logger.start_test(TestCase(name='Second!'))
        self.verify(''',{
"id":"t1"''')

    def test_test_setup(self):
        self.test_start_test()
        setup = Keyword(type=Keyword.SETUP, name='S', start_time=self.start)
        self.logger.start_keyword(setup)
        self.verify(''',
"setup":{''')
        self.logger.end_keyword(setup)
        self.verify('''
"name":"S",
"status":"FAIL",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":0.000000
}''')

    def test_test_teardown(self):
        self.test_test_setup()
        test = TestCase()
        test.teardown.config(name='T', status='PASS')
        self.logger.start_keyword(test.teardown)
        self.verify(''',
"teardown":{''')
        self.logger.end_keyword(test.teardown)
        self.verify('''
"name":"T",
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_test_structure(self):
        self.test_test_setup()
        kw = Keyword(name='K', status='PASS', elapsed_time=1.234567)
        td = Keyword(type=Keyword.TEARDOWN, name='T', status='PASS')
        self.logger.start_keyword(kw)
        self.logger.end_keyword(kw)
        self.verify(''',
"body":[{
"name":"K",
"status":"PASS",
"elapsed_time":1.234567
}''')
        self.logger.start_keyword(kw)
        self.logger.end_keyword(kw)
        self.verify(''',{
"name":"K",
"status":"PASS",
"elapsed_time":1.234567
}''')
        self.logger.start_keyword(td)
        self.logger.end_keyword(td)
        self.verify('''],
"teardown":{
"name":"T",
"status":"PASS",
"elapsed_time":0.000000
}''')
        self.logger.end_test(TestCase())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_keyword(self):
        self.test_start_test()
        kw = Keyword(name='K')
        self.logger.start_keyword(kw)
        self.verify(''',
"body":[{''')
        self.logger.end_keyword(kw)
        self.verify('''
"name":"K",
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_keyword_with_config(self):
        self.test_start_test()
        kw = Keyword(name='K', owner='O', source_name='sn', doc='D', args=['a', 2],
                     assign=['${x}'], tags=['t1', 't2'], timeout='1 day', status='PASS',
                     message="msg", start_time=self.start, elapsed_time=0.654321)
        self.logger.start_keyword(kw)
        self.verify(''',
"body":[{''')
        self.logger.end_keyword(kw)
        self.verify('''
"name":"K",
"owner":"O",
"source_name":"sn",
"args":["a","2"],
"assign":["${x}"],
"tags":["t1","t2"],
"doc":"D",
"timeout":"1 day",
"status":"PASS",
"message":"msg",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":0.654321
}''')

    def test_start_for(self):
        self.test_start_test()
        self.logger.start_for(For())
        self.verify(''',
"body":[{
"type":"FOR"''')

    def test_end_for(self):
        self.test_start_for()
        self.logger.end_for(For(['${x}'], 'IN', ['a', 'b']))
        self.verify(''',
"flavor":"IN",
"assign":["${x}"],
"values":["a","b"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_for_in_enumerate(self):
        self.test_start_test()
        item = For(['${i}', '${x}'], 'IN ENUMERATE', ['a', 'b'], start='1')
        self.logger.start_for(item)
        self.verify(''',
"body":[{
"type":"FOR"''')
        self.logger.end_for(item)
        self.verify(''',
"flavor":"IN ENUMERATE",
"start":"1",
"assign":["${i}","${x}"],
"values":["a","b"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_for_in_zip(self):
        self.test_start_test()
        item = For(['${item}'], 'IN ZIP', ['${X}', '${Y}'], mode='LONGEST', fill='')
        self.logger.start_for(item)
        self.verify(''',
"body":[{
"type":"FOR"''')
        self.logger.end_for(item)
        self.verify(''',
"flavor":"IN ZIP",
"mode":"LONGEST",
"fill":"",
"assign":["${item}"],
"values":["${X}","${Y}"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_for_iteration(self):
        self.test_start_for()
        item = ForIteration(assign={'${x}': 'value'})
        self.logger.start_for_iteration(item)
        self.verify(''',
"body":[{
"type":"ITERATION"'''
        )
        self.logger.end_for_iteration(item)
        self.verify(''',
"assign":{"${x}":"value"},
"status":"FAIL",
"elapsed_time":0.000000
}''')
        self.logger.start_for_iteration(item)
        self.logger.end_for_iteration(item)
        self.verify(''',{
"type":"ITERATION",
"assign":{"${x}":"value"},
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_start_while(self):
        self.test_start_test()
        self.logger.start_while(While())
        self.verify(''',
"body":[{
"type":"WHILE"''')

    def test_end_while(self):
        self.test_start_while()
        self.logger.end_while(While())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_start_while_with_config(self):
        self.test_start_test()
        item = While('$x > 0', '100', 'PASS', 'A message', status='PASS', message='M')
        self.logger.start_while(item)
        self.logger.end_while(item)
        self.verify(''',
"body":[{
"type":"WHILE",
"condition":"$x > 0",
"limit":"100",
"on_limit":"PASS",
"on_limit_message":"A message",
"status":"PASS",
"message":"M",
"elapsed_time":0.000000
}''')

    def test_while_iteration(self):
        self.test_start_while()
        item = WhileIteration(status='SKIP', start_time=self.start)
        self.logger.start_while_iteration(item)
        self.verify(''',
"body":[{
"type":"ITERATION"''')
        self.logger.end_while_iteration(item)
        self.verify(''',
"status":"SKIP",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":0.000000
}''')

    def test_start_if(self):
        self.test_start_test()
        self.logger.start_if(If())
        self.verify(''',
"body":[{
"type":"IF/ELSE ROOT"''')

    def test_end_if(self):
        self.test_start_if()
        self.logger.end_if(If())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_if_branch(self):
        self.test_start_if()
        self.logger.start_if_branch(IfBranch())
        self.verify(''',
"body":[{
"type":"IF"''')
        self.logger.end_if_branch(IfBranch())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')
        self.logger.end_if(If(status='PASS'))
        self.verify('''],
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_if_branch_with_config(self):
        self.test_start_if()
        item = IfBranch(IfBranch.ELSE_IF, '$x > 0')
        self.logger.start_if_branch(item)
        self.verify(''',
"body":[{
"type":"ELSE IF"''')
        self.logger.end_if_branch(item)
        self.verify(''',
"condition":"$x > 0",
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_start_try(self):
        self.test_start_test()
        self.logger.start_try(Try())
        self.verify(''',
"body":[{
"type":"TRY/EXCEPT ROOT"''')

    def test_end_try(self):
        self.test_start_try()
        self.logger.end_try(Try(status='PASS'))
        self.verify(''',
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_try_branch(self):
        self.test_start_try()
        self.logger.start_try_branch(TryBranch())
        self.verify(''',
"body":[{
"type":"TRY"''')
        self.logger.end_try_branch(TryBranch())
        self.verify(''',
"status":"FAIL",
"elapsed_time":0.000000
}''')
        self.logger.end_try(Try(status='PASS'))
        self.verify('''],
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_try_branch_with_config(self):
        self.test_start_try()
        item = TryBranch(TryBranch.EXCEPT, patterns=['x', 'y'], pattern_type='GLOB',
                         assign='${err}')
        self.logger.start_try_branch(item)
        self.verify(''',
"body":[{
"type":"EXCEPT"''')
        self.logger.end_try_branch(item)
        self.verify(''',
"patterns":["x","y"],
"pattern_type":"GLOB",
"assign":"${err}",
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_var(self):
        self.test_start_test()
        var = Var(name='${x}', value=['y'])
        self.logger.start_var(var)
        self.verify(''',
"body":[{
"type":"VAR"''')
        self.logger.end_var(var)
        self.verify(''',
"name":"${x}",
"value":["y"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_var_with_config(self):
        self.test_start_test()
        var = Var(name='${x}', value=['a', 'b'], scope='TEST', separator='',
                  status='PASS', start_time=self.start, elapsed_time=1.2)
        self.logger.start_var(var)
        self.verify(''',
"body":[{
"type":"VAR"''')
        self.logger.end_var(var)
        self.verify(''',
"name":"${x}",
"scope":"TEST",
"separator":"",
"value":["a","b"],
"status":"PASS",
"start_time":"2024-12-03T12:27:00.123456",
"elapsed_time":1.200000
}''')

    def test_return(self):
        self.test_start_test()
        item = Return(values=['a', 'b'])
        self.logger.start_return(item)
        self.verify(''',
"body":[{
"type":"RETURN"''')
        self.logger.end_return(item)
        self.verify(''',
"values":["a","b"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_continue_and_break(self):
        self.test_start_test()
        self.logger.start_continue(Continue())
        self.logger.end_continue(Continue())
        self.logger.start_break(Break())
        self.logger.end_break(Break(status='PASS'))
        self.verify(''',
"body":[{
"type":"CONTINUE",
"status":"FAIL",
"elapsed_time":0.000000
},{
"type":"BREAK",
"status":"PASS",
"elapsed_time":0.000000
}''')

    def test_error(self):
        self.test_start_test()
        item = Error(values=['bad', 'things'])
        self.logger.start_error(item)
        self.logger.message(Message('Something bad happened!'))
        self.logger.end_error(item)
        self.verify(''',
"body":[{
"type":"ERROR",
"body":[{
"type":"MESSAGE",
"message":"Something bad happened!",
"level":"INFO"
}],
"values":["bad","things"],
"status":"FAIL",
"elapsed_time":0.000000
}''')

    def test_message(self):
        self.test_start_test()
        self.logger.message(Message())
        self.verify(''',
"body":[{
"type":"MESSAGE",
"level":"INFO"
}''')
        self.logger.message(Message('Hello!', 'DEBUG', html=True, timestamp=self.start))
        self.verify(''',{
"type":"MESSAGE",
"message":"Hello!",
"level":"DEBUG",
"html":true,
"timestamp":"2024-12-03T12:27:00.123456"
}''')

    def test_no_errors(self):
        self.test_end_suite()
        self.logger.errors([])
        self.verify(''',
"errors":[]''')

    def test_errors(self):
        self.test_end_suite()
        self.logger.errors([Message('Something bad happened!', level='ERROR'),
                            Message('!', level='WARN', html=True, timestamp=self.start)])
        self.verify(''',
"errors":[{
"message":"Something bad happened!",
"level":"ERROR"
},{
"message":"!",
"level":"WARN",
"html":true,
"timestamp":"2024-12-03T12:27:00.123456"
}]''')

    def verify(self, expected, glob=False):
        file = cast(StringIO, self.logger.writer.file)
        actual = file.getvalue()
        file.seek(0)
        file.truncate()
        if glob:
            match = fnmatchcase(actual, expected)
        else:
            match = actual == expected
        if not match:
            raise AssertionError(f'Value does not match.\n\n'
                                 f'Expected:\n{expected}\n\nActual:\n{actual}')


if __name__ == "__main__":
    unittest.main()
