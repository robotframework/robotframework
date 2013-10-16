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
import subprocess
import time

from robot.utils import (ConnectionCache, abspath, encode_to_system,
                         decode_from_system, get_env_vars, timestr_to_secs)
from robot.version import get_version
from robot.api import logger


class Process(object):
    """Robot Framework test library for running processes.

    This library utilizes Python's
    [http://docs.python.org/2.7/library/subprocess.html|subprocess]
    module and its
    [http://docs.python.org/2.7/library/subprocess.html#subprocess.Popen|Popen]
    class.

    The library has following main usages:

    - Running processes in system and waiting for their completion using
      `Run Process` keyword.
    - Starting processes on background using `Start Process`.
    - Waiting started process to complete using `Wait For Process` or
      stopping them with `Terminate Process` or `Terminate All Processes`.

    This library is new in Robot Framework 2.8.

    == Table of contents ==

    - `Specifying command and arguments`
    - `Process configuration`
    - `Active process`
    - `Stopping processes`
    - `Result object`
    - `Using with OperatingSystem library`
    - `Example`

    = Specifying command and arguments =

    Both `Run Process` and `Start Process` accept the command to execute
    and all arguments passed to it as separate arguments. This is convenient
    to use and also allows these keywords to automatically escape possible
    spaces and other special characters in the command or arguments.

    When `running processes in shell`, it is also possible to give the
    whole command to execute as a single string. The command can then
    contain multiple commands, for example, connected with pipes. When
    using this approach the caller is responsible on escaping.

    Examples:
    | `Run Process` | ${progdir}${/}prog.py        | first arg | second         |
    | `Run Process` | script1.sh arg && script2.sh | shell=yes | cwd=${progdir} |

    = Process configuration =

    `Run Process` and `Start Process` keywords can be configured using
    optional `**configuration` keyword arguments. Available configuration
    arguments are listed below and discussed further in sections afterwards.

    | *Name*     | *Explanation*                                         |
    | shell      | Specifies whether to run the command in shell or not  |
    | cwd        | Specifies the working directory.                      |
    | env        | Specifies environment variables given to the process. |
    | env:<name> | Overrides the named environment variable(s) only.     |
    | stdout     | Path of a file where to write standard output.        |
    | stderr     | Path of a file where to write standard error.         |
    | alias      | Alias given to the process.                           |

    Configuration must be given after other arguments passed to these keywords
    and must use syntax `name=value`.

    == Running processes in shell ==

    The `shell` argument specifies whether to run the process in a shell or
    not. By default shell is not used, which means that shell specific
    commands, like `copy` and `dir` on Windows, are not available.

    Giving the `shell` argument any non-false value, such as `shell=True`,
    changes the program to be executed in a shell. It allows using the shell
    capabilities, but can also make the process invocation operating system
    dependent.

    When using a shell it is possible to give the whole command to execute
    as a single string. See `Specifying command and arguments` section for
    more details.

    == Current working directory ==

    By default the child process will be executed in the same directory
    as the parent process, the process running tests, is executed. This
    can be changed by giving an alternative location using the `cwd` argument.
    Forward slashes in the given path are automatically converted to
    backslashes on Windows.

    `Standard output and error streams`, when redirected to files,
    are also relative to the current working directory possibly set using
    the `cwd` argument.

    Example:
    | `Run Process` | prog.exe | cwd=${ROOT}/directory | stdout=stdout.txt |

    == Environment variables ==

    By default the child process will get a copy of the parent process's
    environment variables. The `env` argument can be used to give the
    child a custom environment as a Python dictionary. If there is a need
    to specify only certain environment variable, it is possible to use the
    `env:<name>` format to set or override only that named variables. It is
    also possible to use these two approaches together.

    Examples:
    | `Run Process` | program | env=${environ} |
    | `Run Process` | program | env:PATH=%{PATH}${:}${PROGRAM DIR} |
    | `Run Process` | program | env=${environ} | env:EXTRA=value   |

    == Standard output and error streams ==

    By default processes are run so that their standard output and standard
    error streams are kept in the memory. This works fine normally,
    but if there is a lot of output, the output buffers may get full and
    the program could hang.

    To avoid output buffers getting full, it is possible to use `stdout`
    and `stderr` arguments to specify files on the file system where to
    redirect the outputs. This can also be useful if other processes or
    other keywords need to read or manipulate the outputs somehow.

    Given `stdout` and `stderr` paths are relative to the `current working
    directory`. Forward slashes in the given paths are automatically converted
    to backslashes on Windows.

    As a special feature, it is possible to redirect the standard error to
    the standard output by using `stderr=STDOUT`.

    Regardless are outputs redirected to files or not, they are accessible
    through the `result object` returned when the process ends.

    Examples:
    | ${result} = | `Run Process` | program | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt |
    | `Log Many`  | stdout: ${result.stdout} | stderr: ${result.stderr} |
    | ${result} = | `Run Process` | program | stderr=STDOUT |
    | `Log`       | all output: ${result.stdout} |

    *Note:* The created output files are not automatically removed after
    the test run. The user is responsible to remove them if needed.

    == Alias ==

    A custom name given to the process that can be used when selecting the
    `active process`.

    Example:
    | `Start Process` | program | alias=example |

    = Active process =

    The test library keeps record which of the started processes is currently
    active. By default it is latest process started with `Start Process`,
    but `Switch Process` can be used to select a different one.

    The keywords that operate on started processes will use the active process
    by default, but it is possible to explicitly select a different process
    using the `handle` argument. The handle can be the identifier returned by
    `Start Process` or an explicitly given `alias`.

    = Stopping processes =

    Started processed can be stopped using `Terminate Process` and
    `Terminate All Processes`. The former is used for stopping a selected
    process, and the latter to make sure all processes are stopped, for
    example, in a suite teardown.

    Both keywords use `subprocess`
    [http://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.terminate|terminate()]
    method by default, but can be configured to use
    [http://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.kill|kill()]
    instead.

    Because both `terminate()` and `kill()` methods were added to `subprocess`
    in Python 2.6, stopping processes does not work with Python or Jython 2.5.
    Unfortunately at least beta releases of Jython 2.7
    [http://bugs.jython.org/issue1898|do not seem to support it either].

    Examples:
    | `Terminate Process` | kill=True |
    | `Terminate All Processes` |

    = Result object =

    `Run Process` and `Wait For Process` keywords return a result object
    that contains information about the process execution as its attibutes.
    What is available is documented in the table below.

    | *Attribute* | *Explanation*                             |
    | rc          | Return code of the process as an integer. |
    | stdout      | Contents of the standard output stream.   |
    | stderr      | Contents of the standard error stream.    |
    | stdout_path | Path where stdout was redirected or `None` if not redirected. |
    | stderr_path | Path where stderr was redirected or `None` if not redirected. |

    Example:
    | ${result} =            | `Run Process`         | program               |
    | `Should Be Equal As Integers` | ${result.rc}   |                       |
    | `Should Match`         | ${result.stdout}      | Some t?xt*            |
    | `Should Be Empty`      | ${result.stderr}      |                       |
    | ${stdout} =            | `Get File`            | ${result.stdout_path} |
    | `File Should Be Empty` | ${result.stderr_path} |                       |
    | `Should Be Equal`      | ${result.stdout}      | ${stdout}             |

    = Using with OperatingSystem library =

    The OperatingSystem library also contains keywords for running processes.
    They are not as flexible as the keywords provided by this library, and
    thus not recommended to be used anymore. They may eventually even be
    deprecated.

    There is a name collision because both of these libraries have
    `Start Process` and `Switch Process` keywords. This is handled so that
    if both libraries are imported, the keywords in the Process library are
    used by default. If there is a need to use the OperatingSystem variants,
    it is possible to use `OperatingSystem.Start Process` syntax or use
    the `BuiltIn` keyword `Set Library Search Order` to change the priority.

    Other keywords in the OperatingSystem library can be used freely with
    keywords in the Process library.

    = Example =

    | ***** Settings *****
    | Library    Process
    | Suite Teardown    `Terminate All Processes`    kill=True
    |
    | ***** Test Cases *****
    | Example
    |     `Start Process`    program    arg1   arg2    alias=First
    |     ${handle} =    `Start Process`    command.sh arg | command2.sh   shell=True    cwd=/path
    |     ${result} =    `Run Process`    ${CURDIR}/script.py
    |     `Should Not Contain`    ${result.stdout}    FAIL
    |     `Terminate Process`    ${handle}
    |     ${result} =    `Wait For Process`    First
    |     `Should Be Equal As Integers`   ${result.rc}    0
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self):
        self._processes = ConnectionCache('No active process.')
        self._results = {}
        self._terminate_timeout = 30
        self._kill_timeout = 10

    def run_process(self, command, *arguments, **configuration):
        """Runs a process and waits for it to complete.

        See `Specifying command and arguments` and `Process configuration`
        for more information about the arguments.

        Returns a `result object` containing information about the execution.

        This command does not change the `active process`.
        """
        current = self._processes.current
        try:
            handle = self.start_process(command, *arguments, **configuration)
            return self.wait_for_process(handle)
        finally:
            self._processes.current = current

    def start_process(self, command, *arguments, **configuration):
        """Starts a new process on background.

        See `Specifying command and arguments` and `Process configuration`
        for more information about the arguments.

        Makes the started process new `active process`. Returns an identifier
        that can be used as a handle to active the started process if needed.
        """
        config = ProcessConfig(**configuration)
        executable_command = self._cmd(arguments, command, config.shell)
        logger.info('Starting process:\n%s' % executable_command)
        logger.debug('Process configuration:\n%s' % config)
        process = subprocess.Popen(executable_command,
                                   stdout=config.stdout_stream,
                                   stderr=config.stderr_stream,
                                   stdin=subprocess.PIPE,
                                   shell=config.shell,
                                   cwd=config.cwd,
                                   env=config.env,
                                   universal_newlines=True)
        self._results[process] = ExecutionResult(process,
                                                 config.stdout_stream,
                                                 config.stderr_stream)
        return self._processes.register(process, alias=config.alias)

    def _cmd(self, args, command, use_shell):
        command = [encode_to_system(item) for item in [command] + list(args)]
        if not use_shell:
            return command
        if args:
            return subprocess.list2cmdline(command)
        return command[0]

    def is_process_running(self, handle=None):
        """Checks is the process running or not.

        If `handle` is not given, uses the current `active process`.

        Returns `True` if the process is still running and `False` otherwise.
        """
        return self._processes[handle].poll() is None

    def process_should_be_running(self, handle=None,
                                  error_message='Process is not running.'):
        """Verifies that the process is running.

        If `handle` is not given, uses the current `active process`.

        Fails if the process has stopped.
        """
        if not self.is_process_running(handle):
            raise AssertionError(error_message)

    def process_should_be_stopped(self, handle=None,
                                  error_message='Process is running.'):
        """Verifies that the process is not running.

        If `handle` is not given, uses the current `active process`.

        Fails if the process is still running.
        """
        if self.is_process_running(handle):
            raise AssertionError(error_message)

    def wait_for_process(self, handle=None, timeout=None, handle_timeout='none'):
        """Waits for the process to complete or to reach given timeout.
        Reaching timeout will not fail tests. Instead the action triggered
        by timeout is configured with `handle_timeout` parameter.

        If `handle` is not given, uses the current `active process`.

        `timeout` is a string representing time. It is interpreted
        according to Robot Framework User Guide Appendix `Time Format`

        `handle_timeout` is a string specifying what is done to the process
        when given timeout is reached. Values can be 'none', 'terminate' or 'kill'.
        If 'none' is specified then the process is left running after
        exiting the keyword execution on timeout.

        Returns a `result object` containing information about the execution.
        """
        process = self._processes[handle]
        result = self._results[process]
        logger.info('Waiting for process to complete.')
        result.rc = self._wait_completion(handle, timeout, handle_timeout)
        logger.info('Process completed.')
        return result

    def terminate_process(self, handle=None, kill=False):
        """Terminates the process.

        If `handle` is not given, uses the current `active process`.

        `kill` is a boolean value. If False, a graceful termination is
        attempted and if the process remains running after 30 seconds it
        will be forcefully killed. If True the process will immediately
        be forcefully killed. If the process doesn't shut down in 10
        seconds from killing it, an exception is raised.

        See `Stopping process` for more details.

        Returns a `result object` containing information about the execution.

        Termination timeout and result value are new in Robot Framework 2.8.2
        """
        process = self._processes[handle]
        result = self._results[process]
        if not hasattr(process, 'terminate'):
            raise RuntimeError('Terminating processes is not supported '
                               'by this interpreter version.')
        terminator = self._kill_process if kill else self._terminate_process
        try:
            terminator(process)
            result.rc = process.wait() or 0
            return result
        except OSError:
            if not self._process_is_stopped(process, self._kill_timeout):
                raise
            logger.debug('Ignored OSError because process was stopped.')

    def _kill_process(self, process):
        logger.info('Forcefully killing process.')
        process.kill()
        if not self._process_is_stopped(process, self._kill_timeout):
            raise

    def _terminate_process(self, process):
        logger.info('Gracefully terminating process.')
        process.terminate()
        if not self._process_is_stopped(process, self._terminate_timeout):
            self._kill_process(process)

    def terminate_all_processes(self, kill=False):
        """Terminates all still running processes started by this library.

        `kill` parameter works similar than in `Terminate Process`

        See `Stopping processes` for more details.
        """
        for handle in range(1, len(self._processes) + 1):
            if self.is_process_running(handle):
                self.terminate_process(handle, kill=kill)
        self.__init__()

    def send_signal(self, signal, handle=None):
        if os.sep == '\\':
            raise AssertionError('Process.Send Signal does not work in Windows')
        self._processes[handle].send_signal(self._get_signal(signal))

    def _get_signal(self, signal_string):
        import signal
        return getattr(signal, signal_string)

    def get_process_id(self, handle=None):
        """Returns the process ID (pid) of the process.

        If `handle` is not given, uses the current `active process`.

        Returns the pid assigned by the operating system as an integer.
        Note that with Jython, at least with the 2.5 version, the returned
        pid seems to always be `None`.

        The pid is not the same as the identifier returned by
        `Start Process` that is used internally by this library.
        """
        return self._processes[handle].pid

    def get_process_object(self, handle=None):
        """Return the underlying `subprocess.Popen`  object.

        If `handle` is not given, uses the current `active process`.
        """
        return self._processes[handle]

    def switch_process(self, handle):
        """Makes the specified process the current `active process`.

        The handle can be an identifier returned by `Start Process` or
        the `alias` given to it explicitly.

        Example:
        | `Start Process` | prog1 | alias=process1 |
        | `Start Process` | prog2 | alias=process2 |
        | # currently active process is process2 |
        | `Switch Process` | process1 |
        | # now active process is process 1 |
        """
        self._processes.switch(handle)

    def _wait_completion(self, handle, timeout, handle_timeout):
        timeout_reached = False
        if timeout:
            timeout = timestr_to_secs(timeout)
            timeout_reached = not self._process_is_stopped(self._processes[handle], timeout)
        return self._handle_process_shutdown(handle, timeout_reached, handle_timeout)

    def _process_is_stopped(self, process, timeout):
        max_time = time.time() + timeout
        while time.time() <= max_time:
            if process.poll() is not None:
                return True
            time.sleep(0.1)
        return False

    def _handle_process_shutdown(self, handle, timeout_reached, handle_timeout):
        if timeout_reached:
            if handle_timeout == 'terminate':
                self.terminate_process(handle)
            elif handle_timeout == 'kill':
                self.terminate_process(handle, True)
            else:
                logger.info('Leaving process intact')
                return None
        return self._processes[handle].wait() or 0

class ExecutionResult(object):

    def __init__(self, process, stdout, stderr, rc=None):
        self._process = process
        self.stdout_path = self._get_path(stdout)
        self.stderr_path = self._get_path(stderr)
        self.rc = rc
        self._stdout = None
        self._stderr = None

    def _get_path(self, stream):
        if stream in (subprocess.PIPE, subprocess.STDOUT):
            return None
        return stream.name

    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = self._read_stream(self.stdout_path,
                                             self._process.stdout)
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = self._read_stream(self.stderr_path,
                                             self._process.stderr)
        return self._stderr

    def _read_stream(self, stream_path, stream):
        if stream_path:
            stream = open(stream_path, 'r')
        try:
            return self._format_output(stream.read() if stream else '')
        finally:
            if stream_path:
                stream.close()

    def _format_output(self, output):
        if output.endswith('\n'):
            output = output[:-1]
        return decode_from_system(output)

    def __str__(self):
        return '<result object with rc %d>' % self.rc


class ProcessConfig(object):

    def __init__(self, cwd=None, shell=False, stdout=None, stderr=None,
                 alias=None, env=None, **rest):
        self.cwd = self._get_cwd(cwd)
        self.stdout_stream = self._new_stream(stdout)
        self.stderr_stream = self._get_stderr(stderr, stdout)
        self.shell = bool(shell)
        self.alias = alias
        self.env = self._construct_env(env, rest)

    def _get_cwd(self, cwd):
        if cwd:
            return cwd.replace('/', os.sep)
        return abspath('.')

    def _new_stream(self, name):
        if name:
            name = name.replace('/', os.sep)
            return open(os.path.join(self.cwd, name), 'w')
        return subprocess.PIPE

    def _get_stderr(self, stderr, stdout):
        if stderr:
            if stderr == 'STDOUT' or stderr == stdout:
                if self.stdout_stream == subprocess.PIPE:
                    return subprocess.STDOUT
                return self.stdout_stream
        return self._new_stream(stderr)

    def _construct_env(self, env, rest):
        for key in rest:
            if not key.startswith('env:'):
                raise RuntimeError("'%s' is not supported by this keyword." % key)
            if env is None:
                env = get_env_vars(upper=False)
            env[key[4:]] = rest[key]
        if env:
            env = dict((encode_to_system(key), encode_to_system(env[key]))
                       for key in env)
        return env

    def __str__(self):
        return encode_to_system("""\
cwd = %s
stdout_stream = %s
stderr_stream = %s
shell = %r
alias = %s
env = %r""" % (self.cwd, self.stdout_stream, self.stderr_stream,
               self.shell, self.alias, self.env))
