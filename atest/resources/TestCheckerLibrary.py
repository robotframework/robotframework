import os.path
import re

from robot import utils
from robot.output import readers


class TestCheckerLibrary:
            
    def process_output(self, path):
        try:
            print "Processing output '%s'" % path
            suite, syslog = readers.process_output(path)
            suite.set_names()
        except:
            print 'Processing output failed: ' + utils.get_error_message()
            return None, None
        else:
            return process_suite(suite), syslog

    def get_test_from_suite(self, suite, name):
        tests = self.get_tests_from_suite(suite, name)
        if len(tests) == 1:
            return tests[0]
        elif len(tests) == 0:
            err = "No test '%s' found from suite '%s'"
        else:
            err = "More than one test '%s' found from suite '%s'"
        raise Exception(err % (name, suite.name))
        
    def get_tests_from_suite(self, suite, name=None):
        tests = [ test for test in suite.tests 
                  if name is None or utils.eq(test.name, name) ]
        for subsuite in suite.suites:
            tests.extend(self.get_tests_from_suite(subsuite, name))
        return tests

    def get_suite_from_suite(self, suite, name):
        suites = self.get_suites_from_suite(suite, name)
        if len(suites) == 1:
            return suites[0]
        elif len(suites) == 0:
            err = "No suite '%s' found from suite '%s'"
        else:
            err = "More than one suite '%s' found from suite '%s'"
        raise Exception(err % (name, suite.name))

    def get_suites_from_suite(self, suite, name):
        suites = utils.eq(suite.name, name) and [ suite ] or []
        for subsuite in suite.suites:
            suites.extend(self.get_suites_from_suite(subsuite, name))
        return suites

    def check_test_status(self, test, status=None, message=None):
        """Verifies that test's status and message are as expected.
        
        Expected status and message can be given as parameters. If expected 
        status is not given, expected status and message are read from test's 
        documentation. If documentation doesn't contain any of PASS, FAIL or 
        ERROR, test's status is expected to be PASS. If status is given that is 
        used. Expected message is documetation after given status. Expected 
        message can also be regular expression. In that case expected match 
        starts with REGEXP: , which is ignored in the regexp match.        
        """
        if status is not None:
            test.exp_status = status
        if message is not None:
            test.exp_message = message

        if test.exp_status != test.status:
            if test.exp_status == 'PASS':
                msg = "Test was expected to PASS but it FAILED. "
                msg += "Error message:\n" + test.message
            else:
                msg = "Test was expected to FAIL but it PASSED. "
                msg += "Expected message:\n" + test.exp_message
            raise AssertionError(msg)

        if test.exp_message == test.message:
            return
        if test.exp_message.startswith('REGEXP:'):
            pattern = test.exp_message.replace('REGEXP:', '', 1).strip()
            if re.match(pattern, test.message):
                return
        if test.exp_message.startswith('STARTS:'):
            start = test.exp_message.replace('STARTS:', '', 1).strip()
            if test.message.startswith(start):
                return

        raise AssertionError("Wrong error message\n\n"
                             "Expected:\n%s\n\nActual:\n%s\n"
                             % (test.exp_message, test.message))


    def check_suite_contains_tests(self, suite, *expected_names):
        actual_tests = [ test for test in self.get_tests_from_suite(suite) ]
        tests_msg  = """
Expected tests : %s  
Actual tests   : %s"""  % (str(list(expected_names)), str(actual_tests))
        expected_names = [ utils.normalize(name) for name in expected_names ]
        if len(actual_tests) != len(expected_names):
            raise AssertionError("Wrong number of tests." + tests_msg)
        for test in actual_tests:
            if utils.eq_any(test.name, expected_names):
                self.check_test_status(test)
                expected_names.remove(utils.normalize(test.name))
            else:
                raise AssertionError("Test '%s' was not expected to be run.%s"
                                     % test.name, tests_msg)
        if len(expected_names) != 0:
            raise Exception("Bug in test library")
        
        
    def get_node(self, path, node=None):
        dom =  utils.DomWrapper(path)
        if node is None:
            return dom
        return dom.get_node(node)
        


def process_suite(suite):
    for subsuite in suite.suites:
        process_suite(subsuite)
    for test in suite.tests:
        process_test(test)
    suite.test_count = suite.get_test_count()
    process_keyword(suite.setup)
    process_keyword(suite.teardown)
    return suite
    

def process_test(test):
    if test.doc.count('FAIL') > 0:
        test.exp_status = 'FAIL'
        test.exp_message = test.doc.split('FAIL', 1)[1].strip()
    else:
        test.exp_status = 'PASS'
        test.exp_message = ''    
    test.kws = test.keywords
    test.keyword_count = test.kw_count = len(test.keywords)
    for kw in test.keywords:
        process_keyword(kw)
    process_keyword(test.setup)
    process_keyword(test.teardown)
        
        
def process_keyword(kw):
    if kw is None:
        return
    kw.kws = kw.keywords
    kw.msgs = kw.messages
    kw.message_count = kw.msg_count = len(kw.messages)
    kw.keyword_count = kw.kw_count = len(kw.keywords)
    for subkw in kw.keywords:
        process_keyword(subkw)
