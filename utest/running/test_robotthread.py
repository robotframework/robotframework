import unittest
import sys
from robot.running.timeouts.robotthread import ThreadedRunner

from robot.utils.asserts import *
from thread_resources import *



class TestRunner(unittest.TestCase):
        
    def test_passing(self):
        runner = ThreadedRunner(passing)
        runner.run()
        assert_none(runner.get_result())
        
    def test_returning(self):
        for arg in [ 10, 'hello', ['l','i','s','t'], unittest]:
            runner = ThreadedRunner(returning, args=(arg,))
            runner.run()
            assert_equals(runner.get_result(), arg)

    def test_failing(self):
        runner = ThreadedRunner(failing, args=('hello world',))
        runner.run()
        assert_raises_with_msg(Exception, 'hello world', runner.get_result)

    if sys.platform.startswith('java'):
        from java.lang import Error

        def test_java_failing(self):
            runner = ThreadedRunner(java_failing, args=('hi tellus',))
            runner.run()
            assert_raises_with_msg(Error, 'java.lang.Error: hi tellus', 
                                   runner.get_result)


if __name__ == '__main__':
    unittest.main()
