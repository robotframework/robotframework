#  Copyright 2008-2011 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from __future__ import with_statement
import subprocess
import time
from random import randint
import os
import re
import sys
from robot.libraries import BuiltIn
from robot.utils import html_escape, ArgumentParser
from robot.version import get_version

from Queue import Queue, Empty
from threading import Event
import socket

try:
    from multiprocessing.managers import BaseManager
except ImportError:
    class Communicate(object):

        def __init__(self, address=None, port=None, authkey=None):
           pass

        def connect(self):
           pass

        def stop_server(self):
           pass

        def __getattr__(self, name):
           if not name.startswith('__'):
               raise RuntimeError('Use of messaging is not possible when '+\
                                  'multiprocessing python module is not available.\n'+\
                                  'Multiprocessing module is available in Python >= 2.6')
           return object.__getattr__(self, name)
else:
    def _create_caching_getter(clazz):
        objects = {}
        def get_object(key):
            if key not in objects:
                objects[key] = clazz()
            return objects[key]
        return get_object

    class Communicate(object):

        def __init__(self, address='127.0.0.1', port=2187, authkey='live long and prosper'):
            self._address = address
            self._port = port
            self._authkey = authkey
            self._queue = None
            self._connected = False
            self._server = False

        def set_address(self, address):
            if self._connected:
                raise RuntimeError('Address can not be set as there is already a connection')
            self._address = address

        def set_port(self, port):
            if self._connected:
                raise RuntimeError('Port can not be set as there is already a connection')
            self._port = port

        def connect(self):
            if self._connected:
               return
            try:
               socket.create_connection((self._address, self._port), 0.1).close()
               self._create_manager().connect()
               self._server = False
            except socket.error:
               self._create_manager(_create_caching_getter(Queue),
                                    _create_caching_getter(Event)).start()
               self._server = True
            self._connected = True

        def stop_server(self):
            if self._server:
                self._manager.shutdown()
                self._server = False
            self._connected = False

        def _create_manager(self, queue_getter=None, event_getter=None):
            BaseManager.register('get_queue', queue_getter)
            BaseManager.register('get_event', event_getter)
            self._manager = BaseManager((self._address, self._port), self._authkey)
            return self._manager

        def send_message(self, queue_id, value):
            self._get_queue(queue_id).put(value)

        def receive_message(self, queue_id, timeout):
            return self._get_queue(queue_id).get(timeout=timeout)

        def _get_queue(self, queue_id):
            return self._manager.get_queue(queue_id)

        def wait_for_event(self, event_id):
            return self._get_event(event_id).wait()

        def signal_event(self, event_id):
            return self._get_event(event_id).set()

        def _get_event(self, event_id):
            return self._manager.get_event(event_id)


class Parallel(object):
    """
    Library for executing tests in parallel from inside of a robot test case.
    Tests are executed in subprocesses. 

    You can add arguments to all parallel test runs from `library importing`,
    for a set of parallel tests with `Add Arguments For Parallel Tests` and
    for an individual parallel test by passing the arguments in `Start Parallel Test`.

    The following command line arguments (also from argument files) are automatically 
    passed to parallel tests:
    --loglevel, --runmode, --pythonpath, --variable, --variablefile

    Example:
    | *Settings* |
    | Library | Parallel | pybot |

    | *Test Cases* |
    | Runner |
    |        | Run Parallel Tests | Hello | World |
    |        | [Teardown] | Teardown Parallel |
    | Hello |
    |       | [Tags] | parallel |
    |       | Log    | Hello ${WORLD} |
    | World |
    |       | [Tags] | parallel |
    |       | Log    | ${HELLO} World |
    
    `pybot --exclude parallel --variable HELLO:Hello --variable WORLD:World .`
    """

    def __init__(self, runner_script, *arguments):
        """
        `runner_script` is pybot or jybot or a custom script.

        `arguments` are default arguments given to every test execution.

        Example:
        | Library | Parallel | pybot | --variable | variable:value | --loglevel | DEBUG |
        """
        self._script = runner_script
        self._arguments = self._get_arguments(arguments)
        self._processes = []
        self._communicate = Communicate()
        self._data_source = None

    def _get_arguments(self, additional_arguments):
        options,_ = ArgumentParser(_get_cmd_arguments()).parse_args(sys.argv[1:], argfile='argumentfile', unescape='escape')
        args = []
        for arg in ['loglevel', 'runmode', 'pythonpath', 'variable', 'variablefile']:
           args += self._get_type_arguments(options, arg)
        args += list(additional_arguments)
        return args

    def _get_type_arguments(self, options, key):
        value = options[key]
        args = []
        if value is not None:
            if not isinstance(value, list):
                value = [value]
            for var in value:
                args += ['--%s' % key, var]
        return args  

    def add_arguments_for_parallel_tests(self, *arguments):
        """Adds `arguments` to be used when parallel test is started.

        `arguments` is a list of arguments to pass to parallel executions.

        In the following example variable my_var is used in both of the tests 
        started with the keyword `Run Parallel Tests`:
        | Add Arguments For Parallel Tests | --variable | my_var:value |
        | Run Parallel Tests | Test | Another Test |
        """
        self._arguments += list(arguments)

    def set_data_source_for_parallel_tests(self, data_source):
        """Sets data source which is used when parallel tests are started.

        `data_source` is path to file which contains the test/tests which are
        started/executed with keywords `Start Parallel Test` or `Run Parallel
        Tests`.

        If tests to be executed are in the same suite and Robot Framework 2.5
        or later is used, there is no need to use this keyword as `data_source`
        can be automatically resolved.

        Examples:
        | Set Data Source For Parallel Tests | ${CURDIR}${/}my_parallel_suite.txt |
        | Start Parallel Test | My Parallel Test |
        | Wait All Parallel Tests |
        """   
        self._data_source = data_source

    def start_parallel_test(self, test_name, *arguments):
        """Starts executing test with given `test_name` and `arguments`.

        `arguments` is a list of Robot Framework command line arguments passed to 
        the started test execution. It should not include data source. Use
        `Set Data Source For Parallel Tests` keyword for setting the data
        source. Additional arguments can also be set in library import and with
        `Add Arguments For Parallel Tests` keyword.

        Returns a process object that represents this execution.

        Example:
        | Set Data Source For Parallel Tests | MySuite.txt |
        | Start Parallel Test | Test From My Suite |
        | Set Data Source For Parallel Tests | MyFriendsSuite.txt |
        | Start Parallel Test | Test From My Friends Suite |
        | Wait All Parallel Tests |
        """
        if self._data_source is None:
            self._data_source = BuiltIn.BuiltIn().replace_variables('${SUITE_SOURCE}')
        process = _ParaRobo(test_name, self._data_source, 
                            self._arguments+list(arguments))
        self._add_process(process)
        process.run(self._script)
        return process

    def run_parallel_tests(self, *test_names):
        """Executes all given tests parallel and wait those to be ready.

        Arguments can be set with keyword `Add Arguments For Parallel Tests`
        and data source with keyword `Set Data Source For Parallel Tests`. 

        Example:
        | Add Arguments For Parallel Tests | --variable | SOME_VARIABLE:someValue |
        | Set Data Source For Parallel Tests | MySuite.txt |
        | Run Parallel Tests | My Parallel Test | My Another Parallel Test |
        
        When the parallel tests are from different data sources see the example in `Start Parallel Test`.
        """
        processes = []
        for name in test_names:
            processes += [self.start_parallel_test(name)]
        self.wait_parallel_tests(*processes)

    def wait_parallel_tests(self, *processes):
        """Waits given `processes` to be ready and fails if any of the tests failed.

        `Processes` are list of test execution processes returned from keyword 
        `Start Parallel Test`.
        
        Example
        | ${test 1}= | Start Parallel Test | First Test |
        | ${test 2}= | Start Parallel Test | Test That Runs All The Time |
        | Wait Parallel Tests | ${test 1} |
        | ${test 3}= | Start Parallel Test | Third Test |
        | Wait Parallel Tests | ${test 2} | ${test 3} |
        """
        failed = []
        for process in processes:
            if process.wait() != 0:
                failed += [process.test]
            process.report()
            self._remove_process(process)
        if failed:
            raise AssertionError("Following tests failed:\n%s" % "\n".join(failed))

    def wait_all_parallel_tests(self):
        """Wait all started test executions to be ready and fails if any of those failed."""
        self.wait_parallel_tests(*self._processes)

    def stop_all_parallel_tests(self):
        """Forcefully stops all the test executions.
        
        NOTE: Requires Python 2.6 or later.
        """
        for process in self._processes:
            process.stop_test_execution()
        self._clear_processes()

    def wait_for_event(self, event):
        """Waits until an event has happened.

        `event` is the identifier for the waited event.

        NOTE: Requires Python 2.6 or later.

        Example:
        In one process
        | Wait For Event | my event |
        ...
        In another process
        | Signal Event | my event |
        """
        self._communicate.connect()
        self._communicate.wait_for_event(event)

    def signal_event(self, event):
        """Signals an event.
        If a process is waiting for this event it will stop waiting after the signal.

        `event` is the identifier for the event.

        NOTE: Requires Python 2.6 or later.

        Example:
        In one process
        | Wait For Event | my event |
        ...
        In another process
        | Signal Event | my event |
        """
        self._communicate.connect()
        self._communicate.signal_event(event)

    def send_message_to(self, queue_id, value):
        """Send a message to a message queue.

        `queue_id` is the identifier for the queue.

        `value` is the message. This can be a string, a number or any serializable object.

        NOTE: Requires Python 2.6 or later.

        Example:
        In one process
        | Send Message To | my queue | hello world! |
        ...
        In another process
        | ${message}= | Receive Message From | my queue |
        | Should Be Equal | ${message} | hello world! |
        """
        self._communicate.connect()
        self._communicate.send_message(queue_id, value)

    def receive_message_from(self, queue_id, timeout=None):
        """Receive and consume a message from a message queue.
        By default this keyword will block until there is a message in the queue.

        `queue_id` is the identifier for the queue.

        `timeout` is the time out in seconds to wait.

        Returns the value from the message queue. Throws an exception if timeout expires.

        NOTE: Requires Python 2.6 or later.

        Example:
        In one process
        | Send Message To | my queue | hello world! |
        ...
        In another process
        | ${message}= | Receive Message From | my queue |
        | Should Be Equal | ${message} | hello world! |
        """
        self._communicate.connect()
        timeout = float(timeout) if timeout is not None else None
        return self._communicate.receive_message(queue_id, timeout)

    def set_parallel_communication_server_address(self, address):
        """
        Set a new address for communication server (default is localhost).
        Use this in case the parallel communication is done between remote computers.

        NOTE!
        The same address has to be set in every process that uses the communication server.
        NOTE!
        Requires Python 2.6 or later.
        """
        self._communicate.set_address(address)

    def set_parallel_communication_server_port(self, port):
        """
        Set a new port for communication server (default is 2187).
        Use this in case the default port does not work.

        NOTE!
        The same port has to be set in every process that uses the communication server.
        NOTE!
        Requires Python 2.6 or later.
        """
        self._communicate.set_port(int(port))

    def teardown_parallel(self):
        """
        Use this to ensure that communication server and subprocesses have been stopped and
        that they don't live to the next test.
        A proper place for this is in the teardown section of the main test.

        This will terminate all subprocesses that still are running and
        stop parallel communication server if this process owns
        the communication server and it has not been stopped yet.

        NOTE: Requires Python 2.6 or later.
        """
        for process in self._processes:
            process.kill()
        self._clear_processes()

    def _add_process(self, process):
        self._communicate.connect()
        self._processes += [process]

    def _remove_process(self, process):
        self._processes.remove(process)
        if self._processes == []:
            self._communicate.stop_server()

    def _clear_processes(self):
        self._processes = []
        self._communicate.stop_server()

class _ParaRobo(object):

    def __init__(self, test, data_source, arguments):
        self.test = test
        self._data_source = data_source
        self._args = arguments
        self._built_in = BuiltIn.BuiltIn()
        id = self._create_id()
        self._output = 'output_%s.xml' % id
        self._log = 'log_%s.html' % id
        self._output_dir = self._built_in.replace_variables("${OUTPUT DIR}")
        self._monitor_out = os.path.join(self._output_dir, 'monitor_%s.txt' % id)

    @property
    def _suite_name(self):
        name = os.path.splitext(os.path.basename(self._data_source))[0]
        name = name.split('__', 1)[-1]  # Strip possible prefix
        name = name.replace('_', ' ').strip()
        if name.islower():
            name = name.title()
        return name

    def _create_id(self):
        return "%s_%s" % (randint(0, 10000), time.strftime('%Y%m%d_%H%m%S.')+\
                                    ('%03d' % (int(time.time()*1000) % 1000)))

    def run(self, script):
        self._monitor_file = open(self._monitor_out, 'w')
        cmd = [script,
              '--outputdir', self._output_dir,
               '--output', self._output,
              '--report', 'None',
               '--log', self._log,
              '--monitorcolors', 'off',
              '--test', self.test]+\
              self._args + [self._data_source]
        print "Starting test execution: %s" % " ".join(cmd)
        self._process = subprocess.Popen(cmd,
                                          shell=os.sep == '\\',
                                          stdout=self._monitor_file, 
                                          stderr=self._monitor_file,
                                          env=self._get_environment_variables())

    def _get_environment_variables(self):
        environment_variables = os.environ.copy()
        if environment_variables.has_key("ROBOT_SYSLOG_FILE"):
            del(environment_variables["ROBOT_SYSLOG_FILE"])
        return environment_variables

    def wait(self):
        rc = self._process.wait()
        self._monitor_file.close()
        return rc

    def report(self):
        with open(self._monitor_out, 'r') as monitor_file:
            monitor_output = monitor_file.read()
        try:
            os.remove(self._monitor_out)
        except:
            pass
        match = re.search('^Log:     (.*)$', monitor_output, re.MULTILINE)
        monitor_output = self._replace_stdout_log_message_levels(monitor_output)
        monitor_output = html_escape(monitor_output)
        if match:
            monitor_output = monitor_output.replace(match.group(1), '<a href="%s#test_%s.%s">%s</a>' % (self._log, self._suite_name, self.test, match.group(1)))
        monitor_output = self._add_colours(monitor_output)
        print "*HTML* %s" % monitor_output

    def _replace_stdout_log_message_levels(self, output):
        for level in ['TRACE', 'WARN', 'DEBUG', 'INFO', 'HTML']:
            output = output.replace('\n*%s*' % level, '\n *%s*' % level)
        return output

    def _add_colours(self, output):
        for name, colour in [("PASS", "pass"), ("FAIL", "fail"), ("ERROR", "fail")]:
            output = output.replace(' %s ' % name, ' <span class="%s">%s</span> ' % (colour, name))
        return output

    def stop_test_execution(self):
        try:
            self._process.terminate()
        except AttributeError:
            pass
        self.report()

    def kill(self):
        self._process.kill()


def _get_cmd_arguments():
    import robot
    runner_path = os.path.join(os.path.dirname(os.path.abspath(robot.__file__)),
                               'runner.py')
    with open(runner_path, 'r') as runner_file:
        runner_content = runner_file.read()
    return re.search('"""(.+)"""', runner_content, re.DOTALL).groups()[0]
