import unittest, time, os, sys
from threading import Event
if os.name == 'java':
    import java.lang
    
from robot.utils.asserts import *
from robot.errors import *

from robot.utils.robotthread import Runner, Thread
from thread_resources import *


class TestRunner(unittest.TestCase):
        
    def test_passing(self):
        runner = Runner(passing)
        assert_false(runner.is_done())
        runner.run()
        assert_true(runner.is_done())
        assert_none(runner.get_result())

    def test_notifier(self):
        notifier = Event()
        runner = Runner(passing, notifier=notifier)
        assert_false(runner.is_done())
        assert_false(notifier.isSet())
        runner.run()
        assert_true(runner.is_done())
        assert_true(notifier.isSet())
        
    def test_returning(self):
        for arg in [ 10, 'hello', ['l','i','s','t'], unittest]:
            runner = Runner(returning, args=(arg,))
            assert_false(runner.is_done())
            runner.run()
            assert_true(runner.is_done())
            assert_equals(runner.get_result(), arg)

    def test_failing(self):
        runner = Runner(failing, args=('hello world',))
        assert_false(runner.is_done())
        runner.run()
        assert_true(runner.is_done())
        try:
            runner.get_result()
            fail('get_result did not raise an exception as expected')
        except Exception, err:
            assert_equals(str(err), 'hello world')

    if os.name == 'java':
        def test_java_failing(self):
            runner = Runner(java_failing, args=('hi tellus',))
            assert_false(runner.is_done())
            runner.run()
            assert_true(runner.is_done())
            try:
                runner.get_result()
                fail('get_result did not raise an exception as expected')
            except java.lang.Error, err:
                assert_equals(err.getMessage(), 'hi tellus')


class TestThread(unittest.TestCase):
    
    def test_stoppable(self):
        thread = Thread(Runner(None), stoppable=True)
        assert_true(hasattr(thread, 'stop'))
    
    def test_daemon(self):
        assert_true(Thread(Runner(None), daemon=True).isDaemon())
        assert_false(Thread(Runner(None), daemon=False).isDaemon())

    def test_name(self):
        thread = Thread(Runner(None), name='My Name')
        assert_equals(thread.getName(), 'My Name')
        
    def test_noname(self):        
        name = Thread(Runner(None)).getName()
        assert_equals(type(name), str)
        assert_true(len(name) > 0)

if __name__ == '__main__':
    unittest.main()
