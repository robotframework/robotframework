#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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

import ctypes
import os
import subprocess
import time
import signal as signal_module

from robot.utils import (ConnectionCache, abspath, cmdline2list, console_decode,
                         is_list_like, is_string, is_truthy, NormalizedDict,
                         py2to3, secs_to_timestr, system_decode, system_encode,
                         timestr_to_secs, IRONPYTHON, JYTHON, WINDOWS)
from robot.version import get_version
from robot.api import logger


class Process(object):
    """Robot Framework test library for running processes.

    This library utilizes Python's
    [http://docs.python.org/library/subprocess.html|subprocess]
    module and its
    [http://docs.python.org/library/subprocess.html#popen-constructor|Popen]
    class.

    The library has following main usages:

    - Running processes in system and waiting for their completion using
      `Run Process` keyword.
    - Starting processes on background using `Start Process`.
    - Waiting started process to complete using `Wait For Process` or
      stopping them with `Terminate Process` or `Terminate All Processes`.

    == Table of contents ==

    %TOC%

    = Specifying command and arguments =

    Both `Run Process` and `Start Process` accept the command to execute and
    all arguments passed to the command as separate arguments. This makes usage
    convenient and also allows these keywords to automatically escape possible
    spaces and other special characters in commands and arguments. Notice that
    if a command accepts options that themselves accept values, these options
    and their values must be given as separate arguments.

    When `running processes in shell`, it is also possible to give the whole
    command to execute as a single string. The command can then contain
    multiple commands to be run together. When using this approach, the caller
    is responsible on escaping.

    Examples:
    | `Run Process` | ${tools}${/}prog.py | argument | second arg with spaces |
    | `Run Process` | java | -jar | ${jars}${/}example.jar | --option | value |
    | `Run Process` | prog.py "one arg" && tool.sh | shell=yes | cwd=${tools} |

    Possible non-string arguments are converted to strings automatically.

    = Process configuration =

    `Run Process` and `Start Process` keywords can be configured using
    optional ``**configuration`` keyword arguments. Configuration arguments
    must be given after other arguments passed to these keywords and must
    use syntax like ``name=value``. Available configuration arguments are
    listed below and discussed further in sections afterwards.

    |  = Name =  |                  = Explanation =                      |
    | shell      | Specifies whether to run the command in shell or not. |
    | cwd        | Specifies the working directory.                      |
    | env        | Specifies environment variables given to the process. |
    | env:<name> | Overrides the named environment variable(s) only.     |
    | stdout     | Path of a file where to write standard output.        |
    | stderr     | Path of a file where to write standard error.         |
    | output_encoding | Encoding to use when reading command outputs.    |
    | alias      | Alias given to the process.                           |

    Note that because ``**configuration`` is passed using ``name=value`` syntax,
    possible equal signs in other arguments passed to `Run Process` and
    `Start Process` must be escaped with a backslash like ``name\\=value``.
    See `Run Process` for an example.

    == Running processes in shell ==

    The ``shell`` argument specifies whether to run the process in a shell or
    not. By default shell is not used, which means that shell specific commands,
    like ``copy`` and ``dir`` on Windows, are not available. You can, however,
    run shell scripts and batch files without using a shell.

    Giving the ``shell`` argument any non-false value, such as ``shell=True``,
    changes the program to be executed in a shell. It allows using the shell
    capabilities, but can also make the process invocation operating system
    dependent. Having a shell between the actually started process and this
    library can also interfere communication with the process such as stopping
    it and reading its outputs. Because of these problems, it is recommended
    to use the shell only when absolutely necessary.

    When using a shell it is possible to give the whole command to execute
    as a single string. See `Specifying command and arguments` section for
    examples and more details in general.

    == Current working directory ==

    By default the child process will be executed in the same directory
    as the parent process, the process running tests, is executed. This
    can be changed by giving an alternative location using the ``cwd`` argument.
    Forward slashes in the given path are automatically converted to
    backslashes on Windows.

    `Standard output and error streams`, when redirected to files,
    are also relative to the current working directory possibly set using
    the ``cwd`` argument.

    Example:
    | `Run Process` | prog.exe | cwd=${ROOT}/directory | stdout=stdout.txt |

    == Environment variables ==

    By default the child process will get a copy of the parent process's
    environment variables. The ``env`` argument can be used to give the
    child a custom environment as a Python dictionary. If there is a need
    to specify only certain environment variable, it is possible to use the
    ``env:<name>=<value>`` format to set or override only that named variables.
    It is also possible to use these two approaches together.

    Examples:
    | `Run Process` | program | env=${environ} |
    | `Run Process` | program | env:http_proxy=10.144.1.10:8080 | env:PATH=%{PATH}${:}${PROGDIR} |
    | `Run Process` | program | env=${environ} | env:EXTRA=value |

    == Standard output and error streams ==

    By default processes are run so that their standard output and standard
    error streams are kept in the memory. This works fine normally,
    but if there is a lot of output, the output buffers may get full and
    the program can hang. Additionally on Jython, everything written to
    these in-memory buffers can be lost if the process is terminated.

    To avoid the above mentioned problems, it is possible to use ``stdout``
    and ``stderr`` arguments to specify files on the file system where to
    redirect the outputs. This can also be useful if other processes or
    other keywords need to read or manipulate the outputs somehow.

    Given ``stdout`` and ``stderr`` paths are relative to the `current working
    directory`. Forward slashes in the given paths are automatically converted
    to backslashes on Windows.

    As a special feature, it is possible to redirect the standard error to
    the standard output by using ``stderr=STDOUT``.

    Regardless are outputs redirected to files or not, they are accessible
    through the `result object` returned when the process ends. Commands are
    expected to write outputs using the console encoding, but `output encoding`
    can be configured using the ``output_encoding`` argument if needed.

    If you are not interested in outputs at all, you can explicitly ignore them
    by using a special value ``DEVNULL`` both with ``stdout`` and ``stderr``. For
    example, ``stdout=DEVNULL`` is the same as redirecting output on console
    with ``> /dev/null`` on UNIX-like operating systems or ``> NUL`` on Windows.
    This way the process will not hang even if there would be a lot of output,
    but naturally output is not available after execution either.

    Support for the special value ``DEVNULL`` is new in Robot Framework 3.2.

    Examples:
    | ${result} = | `Run Process` | program | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt |
    | `Log Many`  | stdout: ${result.stdout} | stderr: ${result.stderr} |
    | ${result} = | `Run Process` | program | stderr=STDOUT |
    | `Log`       | all output: ${result.stdout} |
    | ${result} = | `Run Process` | program | stdout=DEVNULL | stderr=DEVNULL |

    Note that the created output files are not automatically removed after
    the test run. The user is responsible to remove them if needed.

    == Output encoding ==

    Executed commands are, by default, expected to write outputs to the
    `standard output and error streams` using the encoding used by the
    system console. If the command uses some other encoding, that can be
    configured using the ``output_encoding`` argument. This is especially
    useful on Windows where the console uses a different encoding than rest
    of the system, and many commands use the general system encoding instead
    of the console encoding.

    The value used with the ``output_encoding`` argument must be a valid
    encoding and must match the encoding actually used by the command. As a
    convenience, it is possible to use strings ``CONSOLE`` and ``SYSTEM``
    to specify that the console or system encoding is used, respectively.
    If produced outputs use different encoding then configured, values got
    through the `result object` will be invalid.

    Examples:
    | `Start Process` | program | output_encoding=UTF-8 |
    | `Run Process`   | program | stdout=${path} | output_encoding=SYSTEM |

    The support to set output encoding is new in Robot Framework 3.0.

    == Alias ==

    A custom name given to the process that can be used when selecting the
    `active process`.

    Examples:
    | `Start Process` | program | alias=example |
    | `Run Process`   | python  | -c | print 'hello' | alias=hello |

    = Active process =

    The test library keeps record which of the started processes is currently
    active. By default it is latest process started with `Start Process`,
    but `Switch Process` can be used to select a different one. Using
    `Run Process` does not affect the active process.

    The keywords that operate on started processes will use the active process
    by default, but it is possible to explicitly select a different process
    using the ``handle`` argument. The handle can be the identifier returned by
    `Start Process` or an ``alias`` explicitly given to `Start Process` or
    `Run Process`.

    = Result object =

    `Run Process`, `Wait For Process` and `Terminate Process` keywords return a
    result object that contains information about the process execution as its
    attributes. The same result object, or some of its attributes, can also
    be get using `Get Process Result` keyword. Attributes available in the
    object are documented in the table below.

    | = Attribute = |             = Explanation =               |
    | rc            | Return code of the process as an integer. |
    | stdout        | Contents of the standard output stream.   |
    | stderr        | Contents of the standard error stream.    |
    | stdout_path   | Path where stdout was redirected or ``None`` if not redirected. |
    | stderr_path   | Path where stderr was redirected or ``None`` if not redirected. |

    Example:
    | ${result} =            | `Run Process`         | program               |
    | `Should Be Equal As Integers` | ${result.rc}   | 0                     |
    | `Should Match`         | ${result.stdout}      | Some t?xt*            |
    | `Should Be Empty`      | ${result.stderr}      |                       |
    | ${stdout} =            | `Get File`            | ${result.stdout_path} |
    | `Should Be Equal`      | ${stdout}             | ${result.stdout}      |
    | `File Should Be Empty` | ${result.stderr_path} |                       |

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is an empty string or equal to ``FALSE``, ``NONE``, ``NO``, ``OFF`` or
    ``0``, case-insensitively. Other strings are considered true regardless
    their value, and other argument types are tested using the same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    True examples:
    | `Terminate Process` | kill=True     | # Strings are generally true.    |
    | `Terminate Process` | kill=yes      | # Same as the above.             |
    | `Terminate Process` | kill=${TRUE}  | # Python ``True`` is true.       |
    | `Terminate Process` | kill=${42}    | # Numbers other than 0 are true. |

    False examples:
    | `Terminate Process` | kill=False    | # String ``false`` is false.   |
    | `Terminate Process` | kill=no       | # Also string ``no`` is false. |
    | `Terminate Process` | kill=${EMPTY} | # Empty string is false.       |
    | `Terminate Process` | kill=${FALSE} | # Python ``False`` is false.   |

    Considering string ``NONE`` false is new in Robot Framework 3.0.3 and
    considering also ``OFF`` and ``0`` false is new in Robot Framework 3.1.

    = Example =

    | ***** Settings *****
    | Library           Process
    | Suite Teardown    `Terminate All Processes`    kill=True
    |
    | ***** Test Cases *****
    | Example
    |     `Start Process`    program    arg1    arg2    alias=First
    |     ${handle} =    `Start Process`    command.sh arg | command2.sh    shell=True    cwd=/path
    |     ${result} =    `Run Process`    ${CURDIR}/script.py
    |     `Should Not Contain`    ${result.stdout}    FAIL
    |     `Terminate Process`    ${handle}
    |     ${result} =    `Wait For Process`    First
    |     `Should Be Equal As Integers`    ${result.rc}    0
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()
    TERMINATE_TIMEOUT = 30
    KILL_TIMEOUT = 10

    def __init__(self):
        self._processes = ConnectionCache('No active process.')
        self._results = {}

    def run_process(self, command, *arguments, **configuration):
        """Runs a process and waits for it to complete.

        ``command`` and ``*arguments`` specify the command to execute and
        arguments passed to it. See `Specifying command and arguments` for
        more details.

        ``**configuration`` contains additional configuration related to
        starting processes and waiting for them to finish. See `Process
        configuration` for more details about configuration related to starting
        processes. Configuration related to waiting for processes consists of
        ``timeout`` and ``on_timeout`` arguments that have same semantics as
        with `Wait For Process` keyword. By default there is no timeout, and
        if timeout is defined the default action on timeout is ``terminate``.

        Returns a `result object` containing information about the execution.

        Note that possible equal signs in ``*arguments`` must be escaped
        with a backslash (e.g. ``name\\=value``) to avoid them to be passed in
        as ``**configuration``.

        Examples:
        | ${result} = | Run Process | python | -c | print 'Hello, world!' |
        | Should Be Equal | ${result.stdout} | Hello, world! |
        | ${result} = | Run Process | ${command} | stderr=STDOUT | timeout=10s |
        | ${result} = | Run Process | ${command} | timeout=1min | on_timeout=continue |
        | ${result} = | Run Process | java -Dname\\=value Example | shell=True | cwd=${EXAMPLE} |

        This keyword does not change the `active process`.
        """
        current = self._processes.current
        timeout = configuration.pop('timeout', None)
        on_timeout = configuration.pop('on_timeout', 'terminate')
        try:
            handle = self.start_process(command, *arguments, **configuration)
            return self.wait_for_process(handle, timeout, on_timeout)
        finally:
            self._processes.current = current

    def start_process(self, command, *arguments, **configuration):
        """Starts a new process on background.

        See `Specifying command and arguments` and `Process configuration`
        for more information about the arguments, and `Run Process` keyword
        for related examples.

        Makes the started process new `active process`. Returns an identifier
        that can be used as a handle to activate the started process if needed.

        Processes are started so that they create a new process group. This
        allows sending signals to and terminating also possible child
        processes. This is not supported on Jython.
        """
        conf = ProcessConfiguration(**configuration)
        command = conf.get_command(command, list(arguments))
        self._log_start(command, conf)
        process = subprocess.Popen(command, **conf.popen_config)
        self._results[process] = ExecutionResult(process, **conf.result_config)
        return self._processes.register(process, alias=conf.alias)

    def _log_start(self, command, config):
        if is_list_like(command):
            command = self.join_command_line(command)
        logger.info(u'Starting process:\n%s' % system_decode(command))
        logger.debug(u'Process configuration:\n%s' % config)

    def is_process_running(self, handle=None):
        """Checks is the process running or not.

        If ``handle`` is not given, uses the current `active process`.

        Returns ``True`` if the process is still running and ``False`` otherwise.
        """
        return self._processes[handle].poll() is None

    def process_should_be_running(self, handle=None,
                                  error_message='Process is not running.'):
        """Verifies that the process is running.

        If ``handle`` is not given, uses the current `active process`.

        Fails if the process has stopped.
        """
        if not self.is_process_running(handle):
            raise AssertionError(error_message)

    def process_should_be_stopped(self, handle=None,
                                  error_message='Process is running.'):
        """Verifies that the process is not running.

        If ``handle`` is not given, uses the current `active process`.

        Fails if the process is still running.
        """
        if self.is_process_running(handle):
            raise AssertionError(error_message)

    def wait_for_process(self, handle=None, timeout=None, on_timeout='continue'):
        """Waits for the process to complete or to reach the given timeout.

        The process to wait for must have been started earlier with
        `Start Process`. If ``handle`` is not given, uses the current
        `active process`.

        ``timeout`` defines the maximum time to wait for the process. It can be
        given in
        [http://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#time-format|
        various time formats] supported by Robot Framework, for example, ``42``,
        ``42 s``, or ``1 minute 30 seconds``. The timeout is ignored if it is
        Python ``None`` (default), string ``NONE`` (case-insensitively), zero,
        or negative.

        ``on_timeout`` defines what to do if the timeout occurs. Possible values
        and corresponding actions are explained in the table below. Notice
        that reaching the timeout never fails the test.

        | = Value = |               = Action =               |
        | continue  | The process is left running (default). |
        | terminate | The process is gracefully terminated.  |
        | kill      | The process is forcefully stopped.     |

        See `Terminate Process` keyword for more details how processes are
        terminated and killed.

        If the process ends before the timeout or it is terminated or killed,
        this keyword returns a `result object` containing information about
        the execution. If the process is left running, Python ``None`` is
        returned instead.

        Examples:
        | # Process ends cleanly      |                  |                  |
        | ${result} =                 | Wait For Process | example          |
        | Process Should Be Stopped   | example          |                  |
        | Should Be Equal As Integers | ${result.rc}     | 0                |
        | # Process does not end      |                  |                  |
        | ${result} =                 | Wait For Process | timeout=42 secs  |
        | Process Should Be Running   |                  |                  |
        | Should Be Equal             | ${result}        | ${NONE}          |
        | # Kill non-ending process   |                  |                  |
        | ${result} =                 | Wait For Process | timeout=1min 30s | on_timeout=kill |
        | Process Should Be Stopped   |                  |                  |
        | Should Be Equal As Integers | ${result.rc}     | -9               |

        Ignoring timeout if it is string ``NONE``, zero, or negative is new
        in Robot Framework 3.2.
        """
        process = self._processes[handle]
        logger.info('Waiting for process to complete.')
        timeout = self._get_timeout(timeout)
        if timeout > 0:
            if not self._process_is_stopped(process, timeout):
                logger.info('Process did not complete in %s.'
                            % secs_to_timestr(timeout))
                return self._manage_process_timeout(handle, on_timeout.lower())
        return self._wait(process)

    def _get_timeout(self, timeout):
        if (is_string(timeout) and timeout.upper() == 'NONE') or not timeout:
            return -1
        return timestr_to_secs(timeout)

    def _manage_process_timeout(self, handle, on_timeout):
        if on_timeout == 'terminate':
            return self.terminate_process(handle)
        elif on_timeout == 'kill':
            return self.terminate_process(handle, kill=True)
        else:
            logger.info('Leaving process intact.')
            return None

    def _wait(self, process):
        result = self._results[process]
        result.rc = process.wait() or 0
        result.close_streams()
        logger.info('Process completed.')
        return result

    def terminate_process(self, handle=None, kill=False):
        """Stops the process gracefully or forcefully.

        If ``handle`` is not given, uses the current `active process`.

        By default first tries to stop the process gracefully. If the process
        does not stop in 30 seconds, or ``kill`` argument is given a true value,
        (see `Boolean arguments`) kills the process forcefully. Stops also all
        the child processes of the originally started process.

        Waits for the process to stop after terminating it. Returns a `result
        object` containing information about the execution similarly as `Wait
        For Process`.

        On Unix-like machines graceful termination is done using ``TERM (15)``
        signal and killing using ``KILL (9)``. Use `Send Signal To Process`
        instead if you just want to send either of these signals without
        waiting for the process to stop.

        On Windows graceful termination is done using ``CTRL_BREAK_EVENT``
        event and killing using Win32 API function ``TerminateProcess()``.

        Examples:
        | ${result} =                 | Terminate Process |     |
        | Should Be Equal As Integers | ${result.rc}      | -15 | # On Unixes |
        | Terminate Process           | myproc            | kill=true |

        Limitations:
        - Graceful termination is not supported on Windows when using Jython.
          Process is killed instead.
        - Stopping the whole process group is not supported when using Jython.
        - On Windows forceful kill only stops the main process, not possible
          child processes.
        """
        process = self._processes[handle]
        if not hasattr(process, 'terminate'):
            raise RuntimeError('Terminating processes is not supported '
                               'by this Python version.')
        terminator = self._kill if is_truthy(kill) else self._terminate
        try:
            terminator(process)
        except OSError:
            if not self._process_is_stopped(process, self.KILL_TIMEOUT):
                raise
            logger.debug('Ignored OSError because process was stopped.')
        return self._wait(process)

    def _kill(self, process):
        logger.info('Forcefully killing process.')
        if hasattr(os, 'killpg'):
            os.killpg(process.pid, signal_module.SIGKILL)
        else:
            process.kill()
        if not self._process_is_stopped(process, self.KILL_TIMEOUT):
            raise RuntimeError('Failed to kill process.')

    def _terminate(self, process):
        logger.info('Gracefully terminating process.')
        # Sends signal to the whole process group both on POSIX and on Windows
        # if supported by the interpreter.
        if hasattr(os, 'killpg'):
            os.killpg(process.pid, signal_module.SIGTERM)
        elif hasattr(signal_module, 'CTRL_BREAK_EVENT'):
            if IRONPYTHON:
                # https://ironpython.codeplex.com/workitem/35020
                ctypes.windll.kernel32.GenerateConsoleCtrlEvent(
                    signal_module.CTRL_BREAK_EVENT, process.pid)
            else:
                process.send_signal(signal_module.CTRL_BREAK_EVENT)
        else:
            process.terminate()
        if not self._process_is_stopped(process, self.TERMINATE_TIMEOUT):
            logger.info('Graceful termination failed.')
            self._kill(process)

    def terminate_all_processes(self, kill=False):
        """Terminates all still running processes started by this library.

        This keyword can be used in suite teardown or elsewhere to make
        sure that all processes are stopped,

        By default tries to terminate processes gracefully, but can be
        configured to forcefully kill them immediately. See `Terminate Process`
        that this keyword uses internally for more details.
        """
        for handle in range(1, len(self._processes) + 1):
            if self.is_process_running(handle):
                self.terminate_process(handle, kill=kill)
        self.__init__()

    def send_signal_to_process(self, signal, handle=None, group=False):
        """Sends the given ``signal`` to the specified process.

        If ``handle`` is not given, uses the current `active process`.

        Signal can be specified either as an integer as a signal name. In the
        latter case it is possible to give the name both with or without ``SIG``
        prefix, but names are case-sensitive. For example, all the examples
        below send signal ``INT (2)``:

        | Send Signal To Process | 2      |        | # Send to active process |
        | Send Signal To Process | INT    |        |                          |
        | Send Signal To Process | SIGINT | myproc | # Send to named process  |

        This keyword is only supported on Unix-like machines, not on Windows.
        What signals are supported depends on the system. For a list of
        existing signals on your system, see the Unix man pages related to
        signal handling (typically ``man signal`` or ``man 7 signal``).

        By default sends the signal only to the parent process, not to possible
        child processes started by it. Notice that when `running processes in
        shell`, the shell is the parent process and it depends on the system
        does the shell propagate the signal to the actual started process.

        To send the signal to the whole process group, ``group`` argument can
        be set to any true value (see `Boolean arguments`). This is not
        supported by Jython, however.
        """
        if os.sep == '\\':
            raise RuntimeError('This keyword does not work on Windows.')
        process = self._processes[handle]
        signum = self._get_signal_number(signal)
        logger.info('Sending signal %s (%d).' % (signal, signum))
        if is_truthy(group) and hasattr(os, 'killpg'):
            os.killpg(process.pid, signum)
        elif hasattr(process, 'send_signal'):
            process.send_signal(signum)
        else:
            raise RuntimeError('Sending signals is not supported '
                               'by this Python version.')

    def _get_signal_number(self, int_or_name):
        try:
            return int(int_or_name)
        except ValueError:
            return self._convert_signal_name_to_number(int_or_name)

    def _convert_signal_name_to_number(self, name):
        try:
            return getattr(signal_module,
                           name if name.startswith('SIG') else 'SIG' + name)
        except AttributeError:
            raise RuntimeError("Unsupported signal '%s'." % name)

    def get_process_id(self, handle=None):
        """Returns the process ID (pid) of the process as an integer.

        If ``handle`` is not given, uses the current `active process`.

        Notice that the pid is not the same as the handle returned by
        `Start Process` that is used internally by this library.
        """
        return self._processes[handle].pid

    def get_process_object(self, handle=None):
        """Return the underlying ``subprocess.Popen`` object.

        If ``handle`` is not given, uses the current `active process`.
        """
        return self._processes[handle]

    def get_process_result(self, handle=None, rc=False, stdout=False,
                           stderr=False, stdout_path=False, stderr_path=False):
        """Returns the specified `result object` or some of its attributes.

        The given ``handle`` specifies the process whose results should be
        returned. If no ``handle`` is given, results of the current `active
        process` are returned. In either case, the process must have been
        finishes before this keyword can be used. In practice this means
        that processes started with `Start Process` must be finished either
        with `Wait For Process` or `Terminate Process` before using this
        keyword.

        If no other arguments than the optional ``handle`` are given, a whole
        `result object` is returned. If one or more of the other arguments
        are given any true value, only the specified attributes of the
        `result object` are returned. These attributes are always returned
        in the same order as arguments are specified in the keyword signature.
        See `Boolean arguments` section for more details about true and false
        values.

        Examples:
        | Run Process           | python             | -c            | print 'Hello, world!' | alias=myproc |
        | # Get result object   |                    |               |
        | ${result} =           | Get Process Result | myproc        |
        | Should Be Equal       | ${result.rc}       | ${0}          |
        | Should Be Equal       | ${result.stdout}   | Hello, world! |
        | Should Be Empty       | ${result.stderr}   |               |
        | # Get one attribute   |                    |               |
        | ${stdout} =           | Get Process Result | myproc        | stdout=true |
        | Should Be Equal       | ${stdout}          | Hello, world! |
        | # Multiple attributes |                    |               |
        | ${stdout}             | ${stderr} =        | Get Process Result |  myproc | stdout=yes | stderr=yes |
        | Should Be Equal       | ${stdout}          | Hello, world! |
        | Should Be Empty       | ${stderr}          |               |

        Although getting results of a previously executed process can be handy
        in general, the main use case for this keyword is returning results
        over the remote library interface. The remote interface does not
        support returning the whole result object, but individual attributes
        can be returned without problems.
        """
        result = self._results[self._processes[handle]]
        if result.rc is None:
            raise RuntimeError('Getting results of unfinished processes '
                               'is not supported.')
        attributes = self._get_result_attributes(result, rc, stdout, stderr,
                                                 stdout_path, stderr_path)
        if not attributes:
            return result
        elif len(attributes) == 1:
            return attributes[0]
        return attributes

    def _get_result_attributes(self, result, *includes):
        attributes = (result.rc, result.stdout, result.stderr,
                      result.stdout_path, result.stderr_path)
        includes = (is_truthy(incl) for incl in includes)
        return tuple(attr for attr, incl in zip(attributes, includes) if incl)

    def switch_process(self, handle):
        """Makes the specified process the current `active process`.

        The handle can be an identifier returned by `Start Process` or
        the ``alias`` given to it explicitly.

        Example:
        | Start Process  | prog1    | alias=process1 |
        | Start Process  | prog2    | alias=process2 |
        | # currently active process is process2 |
        | Switch Process | process1 |
        | # now active process is process1 |
        """
        self._processes.switch(handle)

    def _process_is_stopped(self, process, timeout):
        stopped = lambda: process.poll() is not None
        max_time = time.time() + timeout
        while time.time() <= max_time and not stopped():
            time.sleep(min(0.1, timeout))
        return stopped()

    def split_command_line(self, args, escaping=False):
        """Splits command line string into a list of arguments.

        String is split from spaces, but argument surrounded in quotes may
        contain spaces in them. If ``escaping`` is given a true value, then
        backslash is treated as an escape character. It can escape unquoted
        spaces, quotes inside quotes, and so on, but it also requires using
        double backslashes when using Windows paths.

        Examples:
        | @{cmd} = | Split Command Line | --option "value with spaces" |
        | Should Be True | $cmd == ['--option', 'value with spaces'] |

        New in Robot Framework 2.9.2.
        """
        return cmdline2list(args, escaping=escaping)

    def join_command_line(self, *args):
        """Joins arguments into one command line string.

        In resulting command line string arguments are delimited with a space,
        arguments containing spaces are surrounded with quotes, and possible
        quotes are escaped with a backslash.

        If this keyword is given only one argument and that is a list like
        object, then the values of that list are joined instead.

        Example:
        | ${cmd} = | Join Command Line | --option | value with spaces |
        | Should Be Equal | ${cmd} | --option "value with spaces" |

        New in Robot Framework 2.9.2.
        """
        if len(args) == 1 and is_list_like(args[0]):
            args = args[0]
        return subprocess.list2cmdline(args)


class ExecutionResult(object):

    def __init__(self, process, stdout, stderr, rc=None, output_encoding=None):
        self._process = process
        self.stdout_path = self._get_path(stdout)
        self.stderr_path = self._get_path(stderr)
        self.rc = rc
        self._output_encoding = output_encoding
        self._stdout = None
        self._stderr = None
        self._custom_streams = [stream for stream in (stdout, stderr)
                                if self._is_custom_stream(stream)]

    def _get_path(self, stream):
        return stream.name if self._is_custom_stream(stream) else None

    def _is_custom_stream(self, stream):
        return stream not in (subprocess.PIPE, subprocess.STDOUT)

    @property
    def stdout(self):
        if self._stdout is None:
            self._read_stdout()
        return self._stdout

    @property
    def stderr(self):
        if self._stderr is None:
            self._read_stderr()
        return self._stderr

    def _read_stdout(self):
        self._stdout = self._read_stream(self.stdout_path, self._process.stdout)

    def _read_stderr(self):
        self._stderr = self._read_stream(self.stderr_path, self._process.stderr)

    def _read_stream(self, stream_path, stream):
        if stream_path:
            stream = open(stream_path, 'rb')
        elif not self._is_open(stream):
            return ''
        try:
            content = stream.read()
        except IOError:  # http://bugs.jython.org/issue2218
            return ''
        finally:
            if stream_path:
                stream.close()
        return self._format_output(content)

    def _is_open(self, stream):
        return stream and not stream.closed

    def _format_output(self, output):
        output = console_decode(output, self._output_encoding, force=True)
        output = output.replace('\r\n', '\n')
        if output.endswith('\n'):
            output = output[:-1]
        return output

    def close_streams(self):
        standard_streams = self._get_and_read_standard_streams(self._process)
        for stream in standard_streams + self._custom_streams:
            if self._is_open(stream):
                stream.close()

    def _get_and_read_standard_streams(self, process):
        stdin, stdout, stderr = process.stdin, process.stdout, process.stderr
        if stdout:
            self._read_stdout()
        if stderr:
            self._read_stderr()
        return [stdin, stdout, stderr]

    def __str__(self):
        return '<result object with rc %d>' % self.rc


@py2to3
class ProcessConfiguration(object):

    def __init__(self, cwd=None, shell=False, stdout=None, stderr=None,
                 output_encoding='CONSOLE', alias=None, env=None, **rest):
        self.cwd = self._get_cwd(cwd)
        self.stdout_stream = self._new_stream(stdout)
        self.stderr_stream = self._get_stderr(stderr, stdout, self.stdout_stream)
        self.shell = is_truthy(shell)
        self.alias = alias
        self.output_encoding = output_encoding
        self.env = self._construct_env(env, rest)

    def _get_cwd(self, cwd):
        if cwd:
            return cwd.replace('/', os.sep)
        return abspath('.')

    def _new_stream(self, name):
        if name == 'DEVNULL':
            return open(os.devnull, 'w')
        if name:
            name = name.replace('/', os.sep)
            return open(os.path.join(self.cwd, name), 'w')
        return subprocess.PIPE

    def _get_stderr(self, stderr, stdout, stdout_stream):
        if stderr and stderr in ['STDOUT', stdout]:
            if stdout_stream != subprocess.PIPE:
                return stdout_stream
            return subprocess.STDOUT
        return self._new_stream(stderr)

    def _construct_env(self, env, extra):
        env = self._get_initial_env(env, extra)
        if env is None:
            return None
        if WINDOWS:
            env = NormalizedDict(env, spaceless=False)
        self._add_to_env(env, extra)
        if WINDOWS:
            env = dict((key.upper(), env[key]) for key in env)
        return env

    def _get_initial_env(self, env, extra):
        if env:
            return dict((system_encode(k), system_encode(env[k])) for k in env)
        if extra:
            return os.environ.copy()
        return None

    def _add_to_env(self, env, extra):
        for key in extra:
            if not key.startswith('env:'):
                raise RuntimeError("Keyword argument '%s' is not supported by "
                                   "this keyword." % key)
            env[system_encode(key[4:])] = system_encode(extra[key])

    def get_command(self, command, arguments):
        command = [system_encode(item) for item in [command] + arguments]
        if not self.shell:
            return command
        if arguments:
            return subprocess.list2cmdline(command)
        return command[0]

    @property
    def popen_config(self):
        config = {'stdout': self.stdout_stream,
                  'stderr': self.stderr_stream,
                  'stdin': subprocess.PIPE,
                  'shell': self.shell,
                  'cwd': self.cwd,
                  'env': self.env}
        # Close file descriptors regardless the Python version:
        # https://github.com/robotframework/robotframework/issues/2794
        if not WINDOWS:
            config['close_fds'] = True
        if not JYTHON:
            self._add_process_group_config(config)
        return config

    def _add_process_group_config(self, config):
        if hasattr(os, 'setsid'):
            config['preexec_fn'] = os.setsid
        if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
            config['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP

    @property
    def result_config(self):
        return {'stdout': self.stdout_stream,
                'stderr': self.stderr_stream,
                'output_encoding': self.output_encoding}

    def __unicode__(self):
        return """\
cwd:     %s
shell:   %s
stdout:  %s
stderr:  %s
alias:   %s
env:     %s""" % (self.cwd, self.shell, self._stream_name(self.stdout_stream),
                  self._stream_name(self.stderr_stream), self.alias, self.env)

    def _stream_name(self, stream):
        if hasattr(stream, 'name'):
            return stream.name
        return {subprocess.PIPE: 'PIPE',
                subprocess.STDOUT: 'STDOUT'}.get(stream, stream)
