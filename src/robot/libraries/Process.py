#  Copyright 2008-2013 Nokia Siemens Networks Oyj
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

import os
import signal
import subprocess
import sys
import tempfile

from robot.utils import ConnectionCache
from robot.version import get_version


class Process(object):
    """Robot Framework test library for running processes.

    This library utilizes Python's
    [http://docs.python.org/2.7/library/subprocess.html#subprocess.Popen|Subprocess API and its Popen class].

    The library has following main usages:

    - Starting a processes, and managing their handles, stdouts and stderrs
    - Stopping processes started by this library
    - Switching between processes
    - Checking process status.

    == Table of contents ==

    - `Configurations`
    - `Example`
    - `Active process`
    - `ExecutionResult`

    = Configurations =
    `Run Process` and `Start New Process` keywords can be given several named
    arguments, which are listed below. Default values in the parenthesis.

     - `cwd` specifies if program's directory is used as cwd  (`False`)
     - `shell` specifies if shell is used for program execution (`False`)
     - `stdout` is a file handle for standard output
     - `stderr` is a file handle for standard error
     - `stdin` is a file handle for standard input
     - `alias` is a name for the process (`None`).

    = Example =
    The following example demonstrates library's main usages as stated above.

    | *** Settings *** |  |  |  |  |
    | Library | Process |  |  |  |
    |  |  |  |  |  |
    | *** Test Cases *** |  |  |  |  |
    | Example |  |  |  |  |
    | ${handle1}= | `Start New Process` | /path/command.sh    | shell=True  | cwd=/path |
    | ${handle2}= | `Start New Process` | ${CURDIR}${/}mytool   | shell=True |   |
    | ${result1}=  | `Wait For Process` | ${handle1} |    |  |
    |  | `Terminate Process` | ${handle2} |    |   |
    |  | `Process Should Be Dead` | ${handle2} |    |   |
    |  | [Teardown] | `Kill All Processes` |    |   |

    = Active process =
    Many of the library keywords have `handle` as optional argument. This means
    that if argument `handle` is NOT given, then current active process is used.

    = ExecutionResult =
    This object contains information about the process execution.

    Included information is:

    - `stdout` standard output file handle
    - `stderr` standard error file handle
    - `exit_code` from the process, `None` during execution.
    """

    ROBOT_LIBRARY_SCOPE='GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self):
        self._started_processes = ConnectionCache()
        self._logs = dict()
        self._tempdir = tempfile.mkdtemp(suffix="processlib")

    def run_process(self, command, *args, **conf):
        """This keyword runs a process and waits for it to terminate.

        The `command` is a child program which is started in a new process,
        `args` are arguments for the `command` and `conf` are arguments for the
        Subprocess API (see `Configurations`).

        Finally it switches back to active process.
        """
        active_process_index = self._started_processes.current_index
        try:
            p = self.start_new_process(command, *args, **conf)
            return self.wait_for_process(p)
        finally:
            self._started_processes.switch(active_process_index)

    def start_new_process(self, command, *args, **conf):
        """This keyword starts a new process.

        The `command` is a child program which is started in a new process,
        `args` are arguments for the `command` and `conf` are arguments for the
        Subprocess API (see `Configurations`).

        Returns process index on success.

        Examples:

        | $handle1}= | `Start New Process` | /bin/script.sh | |
        | $handle2}= | `Start New Process` | totals | |
        """
        config = NewProcessConfig(self._tempdir, **conf)
        p = subprocess.Popen(self._cmd(args, command, config.shell),
                             stdout=config.stdout_stream,
                             stderr=config.stderr_stream,
                             stdin=subprocess.PIPE,
                             shell=config.shell,
                             cwd=config.cwd)
        self._logs[p] = ExecutionResult(config.stdout_stream.name,
                                        config.stderr_stream.name)
        return self._started_processes.register(p, alias=config.alias)

    def _cmd(self, args, command, use_shell):
        cmd = [command] + [str(i) for i in args]
        if use_shell and args:
            cmd = subprocess.list2cmdline(cmd)
        elif use_shell:
            cmd = command
        return cmd

    def process_is_alive(self, handle=None):
        """Returns a running status of process with `handle`. Argument `handle`
        is optional, if `None` then the current process is used.

        Return value is either `True` or `False`
        """
        return self._process(handle).poll() is None

    def process_should_be_alive(self, handle=None):
        """Assertion keyword, which expects that process with `handle` is alive.
        Argument `handle` is optional, if `None` then the current process is used.

        Check is done using `Process Is Alive` keyword.

        Raises an error if process is dead.
        """
        if not self.process_is_alive(handle):
            raise AssertionError('Process is not alive')

    def process_should_be_dead(self, handle=None):
        """Assertion keyword, which expects that process with `handle` is dead.
        Argument `handle` is optional, if left then the current process is used.

        Check is done using `Process Is Alive` keyword.

        Raises an error if process is alive.
        """
        if self.process_is_alive(handle):
            raise AssertionError('Process is alive')

    def wait_for_process(self, handle=None):
        """This waits for process with `handle` to complete its execution.

        Argument `handle` is optional, if left then the current process is used.

        Returns an `ExecutionResult` object.

        Examples:

        | ${output}= | `Wait For Process` | |
        | Should Be Equal As Integers | ${output.exit_code} | 0 |
        | Should Match | ${output.stdout} | `*text in the out*` |
        | Should Match | ${output.stderr} | |
        """
        process = self._process(handle)
        result = self._logs[process]
        result.exit_code = process.wait()
        return result

    def terminate_process(self, handle=None, kill=False):
        """This keyword terminates process using either `Subprocess` `kill()`
        or `terminate()`, which can be selected using `kill` argument.

        Argument `handle` is optional, if `None` then the current process is used.

        Examples:

        | `Terminate Process` | | # Terminates the current process |
        | `Terminate Process` | ${handle3} | |
        """
        process = self._process(handle)

        # This should be enough to check if we are dealing with <2.6 Python
        if not hasattr(process,'kill'):
            self._terminate_process(process)
            return
        if kill:
            process.kill()
        else:
            process.terminate()

    def _terminate_process(self, theprocess):
        if sys.platform == 'win32':
            import ctypes
            PROCESS_TERMINATE = 1
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_TERMINATE,
                                                        False,
                                                        theprocess.pid)
            ctypes.windll.kernel32.TerminateProcess(handle, -1)
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            pid = theprocess.pid
            if pid is not None:
                os.kill(pid, signal.SIGKILL)
            else:
                raise AssertionError('None Pid - can not kill process!')

    def kill_all_processes(self):
        """This keyword terminates all processes started by the library.
        """
        for handle in range(len(self._started_processes._connections)):
            if self.process_is_alive(handle):
                self.terminate_process(handle, kill=True)

    def get_process_id(self, handle=None):
        """Returns a process ID of process with `handle`.

        Argument `handle` is optional, if `None` then the current process is used.

        Return value is a integer value.

        Examples:

        | ${pid}= | `Get Process Id` | | # Gets PID of the active process | |
        | ${handle1}= | `Start New Process` | python -c "print 'hello'" | shell=True | alias=hello |
        | ${pid_1}= | `Get Process Id` | ${handle1} | # Gets PID with `handle1` | |
        | ${pid_2}= | `Get Process Id` | ${handle1} | # Gets PID with alias `hello` | |
        | Should Be Equal As Integers | ${pid_1} | ${pid_2} |  | |
        """
        return self._process(handle).pid

    def input_to_process(self, msg, handle=None):
        """This keyword can be used to communicate with the process with `handle`.

        Argument `handle` is optional, if `None` then the current process is used.

        Examples:

        | `Wait For Process` | ${handle3} | |
        | `Input To Process` | ${PASSWORD} | ${handle3} |
        """
        self._process(handle).communicate(msg+'\n')

    def switch_active_process(self, handle):
        """This keyword switches active process into process with `handle`.

        Examples:

        | Run Keyword And Expect Error | `Switch Active Process` | |
        | Run Keyword And Expect Error | `Switch Active Process` | ${nonexistent_handle} |
        | `Switch Active Process` | ${handle1} | |
        """
        self._started_processes.switch(handle)

    def _process(self, handle):
        if handle:
            process,_ = self._started_processes.get_connection(handle)
        else:
            process = self._started_processes.current
        return process


class ExecutionResult(object):

    _stdout = _stderr = None

    def __init__(self, stdout_name, stderr_name, exit_code=None):
        self._stdout_name = stdout_name
        self._stderr_name = stderr_name
        self.exit_code = exit_code

    @property
    def stdout(self):
        if self._stdout is None:
            with open(self._stdout_name,'r') as f:
                self._stdout = f.read()
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            with open(self._stderr_name,'r') as f:
                self._stderr = f.read()
        return self._stderr

    def __str__(self):
        return """\
stdout_name : %s
stderr_name : %s
exit_code   : %d""" % (self._stdout_name, self._stderr_name, self.exit_code)


class NewProcessConfig(object):

    FILE_INDEX = 0

    def __init__(self, tempdir, cwd=None,
                 shell=False, stdout=None,
                 stderr=None, alias=None):
        self._tempdir = tempdir
        self.cwd = cwd or os.path.abspath(os.curdir)
        self.stdout_stream = self._new_stream(stdout, 'stdout')
        self.stderr_stream = self._get_stderr(stderr, stdout)
        self.shell = bool(shell)
        self.alias = alias

    def _new_stream(self, name, postfix):
        if name:
            return open(os.path.join(self.cwd, name), 'w')
        return self._get_temp_file(postfix)

    def _get_stderr(self, stderr, stdout):
        if stderr:
            if stderr == 'STDOUT' or stderr == stdout:
               return self.stdout_stream
        return self._new_stream(stderr, 'stderr')

    def _get_temp_file(self, suffix):
        filename = 'tmp_logfile_%d_%s.out' % (NewProcessConfig.FILE_INDEX, suffix)
        NewProcessConfig.FILE_INDEX += 1
        return open(os.path.join(self._tempdir, filename), 'w')
