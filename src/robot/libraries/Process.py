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

from robot.utils import ConnectionCache, encode_to_system, decode_from_system
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

    TODO: Is the below comment still true? Document issues with Jython and IPY.
    Note that this library has not been designed for
    [http://ironpython.codeplex.com/|IronPython] compatibility.

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
    | `Run Process` | ${progdir}/prog.exe      | first arg | second         |
    | `Run Process` | prog1.py arg && prog2.py | shell=yes | cwd=${progdir} |

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

    Example:
    | `Run Process` | prog.exe | cwd=c:\\\\temp |

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
    the program hang.

    To avoid output buffers getting full, it is possible to use `stdout`
    and `stderr` arguments to specify files on the file system where to
    redirect the outputs. This can also be useful if other processes or
    other keywords need to read or manipulate the outputs somehow.

    As a special feature, it is possible to redirect the standard error to
    the standard output by using `stderr=STDOUT`.

    Regardless are outputs redirected to files or not, they are accessible
    through the `result object` returned when the process ends.

    Examples:
    | ${result} = | `Run Process` | program | stdout=${TEMPDIR}/stdout.txt | stderr=${TEMPDIR}/stderr.txt |
    | `Log Many`  | stdout: ${result.stdout} | stderr: ${result.stderr} |
    | ${result} = | `Run Process` | program | stderr=STDOUT |
    | `Log`       | all output: ${result.stdout} |

    TODO:
    - Document issues with Jython/Ipy.
    - Document are stdout/stderr files relative to the cwd or what.
    - Replace / with \ in stdout/stderr paths on Windows? Also in command?

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

    Because both `terminate()` and `kill()` were added to `subprocess` in
    Python 2.6, stopping processes does not work with Python or Jython 2.5.

    TODO: Has Jython 2.7 been tested?

    Examples:
    | `Terminate Process` | kill=True |
    | `Terminate All Processes` |

    = Result object =

    `Run Process` and `Wait For Process` keywords return a result object
    that contains information about the process execution as its attibutes.
    What is available is documented in the table below.

    | *Attribute* | *Explanation*                                 |
    | stdout      | Contents of the standard output stream.       |
    | stderr      | Contents of the standard error stream.        |
    | stdout_path | Path of the file where stdout was redirected. |
    | stderr_path | Path of the file where stderr was redirected. |
    | exit_code   | Return code of the process.                   |

    TODO:
    - value of stdxxx_path when no redirection?
    - is exit_code integer or string? can it be None?
    - why exit_code and not return_core or rc?

    Example:
    | ${result} =            | `Run Process`         | program               |
    | `Log`                  | ${result.exit_code}   |                       |
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
    |     Should Be Equal    ${result.exit_code}    0

    TODO: Is the above exit_code check ok?
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self):
        self._started_processes = ConnectionCache('No started processes.')
        self._results = {}

    def run_process(self, command, *arguments, **configuration):
        """Runs a process and waits for it to complete.

        See `Specifying command and arguments` and `Process configuration`
        for more information about the arguments.

        Returns a `result object` containing information about the execution.

        This command does not change the `active process`.
        """
        active_process_index = self._started_processes.current_index
        try:
            p = self.start_process(command, *arguments, **configuration)
            return self.wait_for_process(p)
        finally:
            if active_process_index is not None:
                self._started_processes.switch(active_process_index)

        # TODO: Apparently the process is still left to the cache

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
        return self._started_processes.register(process, alias=config.alias)

    def _cmd(self, args, command, use_shell):
        command = [encode_to_system(item) for item in [command] + list(args)]
        if not use_shell:
            return command
        if args:
            return subprocess.list2cmdline(command)
        return command[0]

    def is_process_running(self, handle=None):
        """Checks is the process running or not.

        If `handle`is not given, uses the current `active process`.

        Returns `True` if the process is still running and `False` otherwise.
        """
        return self._process(handle).poll() is None

    def process_should_be_running(self, handle=None,
                                  error_message='Process is not running.'):
        """Verifies that the process is running.

        If `handle`is not given, uses the current `active process`.

        Fails if the process has stopped.
        """
        if not self.is_process_running(handle):
            raise AssertionError(error_message)

    def process_should_be_stopped(self, handle=None,
                                  error_message='Process is running.'):
        """Verifies that the process is not running.

        If `handle`is not given, uses the current `active process`.

        Fails if the process is still running.
        """
        if self.is_process_running(handle):
            raise AssertionError(error_message)

    def wait_for_process(self, handle=None):
        """Waits for the process to complete.

        If `handle`is not given, uses the current `active process`.

        Returns a `result object` containing information about the execution.
        """
        process = self._process(handle)
        result = self._results[process]
        logger.info('Waiting for process to complete.')
        result.exit_code = process.wait()
        logger.info('Process completed.')
        return result

    def terminate_process(self, handle=None, kill=False):
        """Terminates the process.

        If `handle`is not given, uses the current `active process`.

        See `Stopping process` for more details.
        """
        process = self._process(handle)

        # TODO: Is pre 2.6 support needed? If yes, and it works, docs need to be changed.
        # This should be enough to check if we are dealing with <2.6 Python
        if not hasattr(process, 'kill'):
            self._terminate_process(process)
            return
        try:
            if kill:
                logger.info('calling subprocess.Popen.kill()')
                process.kill()
            else:
                logger.info('calling subprocess.Popen.terminate()')
                process.terminate()
        except OSError:
            logger.debug('OSError during process termination')
            if process.poll() is None:
                logger.debug('Process still alive raising exception')
                raise
            logger.debug('Process is not executing - consuming OSError')

    def _terminate_process(self, theprocess):
        if sys.platform == 'win32':
            logger.info('terminating process using ctypes.windll.kernel32')
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
                logger.info('terminating process using os.kill')
                os.kill(pid, signal.SIGKILL)
            else:
                raise AssertionError('None Pid - can not kill process!')

    def terminate_all_processes(self, kill=True):
        """Terminates all still running processes started by this library.

        See `Stopping processes` for more details.
        """
        for handle in range(len(self._started_processes._connections)):
            if self.is_process_running(handle):
                self.terminate_process(handle, kill=kill)

    def get_process_id(self, handle=None):
        """Returns the process ID (pid) of the process.

        If `handle`is not given, uses the current `active process`.

        Returns the pid assigned by the operating system as an integer.

        The pid is not the same as the identifier returned by
        `Start Process` that is used internally by this library.
        """
        return self._process(handle).pid

    def get_process_object(self, handle=None):
        """Return the underlying `subprocess.Popen`  object.

        If `handle`is not given, uses the current `active process`.
        """
        return self._process(handle)

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
        self._started_processes.switch(handle)

    def _process(self, handle):
        # TODO: Handle errors when using invalid handle or when no processes running.
        if handle:
            return self._started_processes.get_connection(handle)
        return self._started_processes.current


class ExecutionResult(object):
    _stdout = _stderr = _process = None

    def __init__(self, process, stdout, stderr, exit_code=None):
        self._process = process
        self.stdout_path = self._construct_stdout_path(stdout)
        self.stderr_path = self._construct_stderr_path(stderr)
        self.exit_code = exit_code

    def _construct_stdout_path(self, stdout):
        return stdout.name if stdout != subprocess.PIPE else None

    def _construct_stderr_path(self, stderr):
        if stderr == subprocess.PIPE:
            return None
        if stderr == subprocess.STDOUT:
            return subprocess.STDOUT
        return stderr.name

    @property
    def stdout(self):
        if self._stdout is None:
            self._stdout = self._construct_stdout()
        if self._stdout.endswith('\n'):
            self._stdout = self._stdout[:-1]
        return self._stdout

    def _construct_stdout(self):
        if not self.stdout_path:
            return decode_from_system(self._process.stdout.read())
        with open(self.stdout_path, 'r') as f:
            return decode_from_system(f.read())

    @property
    def stderr(self):
        if self._stderr is None:
            self._stderr = self._construct_stderr()
        if self._stderr.endswith('\n'):
            self._stderr = self._stderr[:-1]
        return self._stderr

    def _construct_stderr(self):
        if self.stderr_path == subprocess.STDOUT:
            return self.stdout
        elif not self.stderr_path:
            return self._process.stderr.read()
        with open(self.stderr_path, 'r') as f:
            return f.read()

    # TODO: attribute names are wrong. should also somehow show that stdout and stderr are available
    def __str__(self):
        return """\
stdout_name : %s
stderr_name : %s
exit_code   : %d""" % (self.stdout_path, self.stderr_path, self.exit_code)


class ProcessConfig(object):

    def __init__(self, cwd=None, shell=False, stdout=None, stderr=None,
                 alias=None, env=None, **rest):
        self.cwd = cwd or os.path.abspath(os.curdir)
        self.stdout_stream = self._new_stream(stdout, 'stdout')
        self.stderr_stream = self._get_stderr(stderr, stdout)
        self.shell = bool(shell)
        self.alias = alias
        self.env = self._construct_env(env, rest)

    def _new_stream(self, name, postfix):
        if name == 'PIPE':
            return subprocess.PIPE
        if name:
            return open(os.path.join(self.cwd, name), 'w')
        return subprocess.PIPE

    def _get_stderr(self, stderr, stdout):
        if stderr:
            if stderr == 'STDOUT' or stderr == stdout:
                if self.stdout_stream == subprocess.PIPE:
                    return subprocess.STDOUT
                return self.stdout_stream
        return self._new_stream(stderr, 'stderr')

    def _construct_env(self, env, rest):
        for key in rest:
            if not key.startswith('env:'):
                raise RuntimeError("'%s' is not supported by this keyword." % key)
            if env is None:
                env = os.environ.copy()
            env[key[4:]] = rest[key]
        if env:
            env = dict((encode_to_system(key), encode_to_system(env[key]))
                       for key in env)
        return env

    # TODO: Is this needed?
    def __str__(self):
        return encode_to_system("""
cwd = %s
stdout_stream = %s
stderr_stream = %s
shell = %r
alias = %s
env = %r""" % (self.cwd, self.stdout_stream, self.stderr_stream,
            self.shell, self.alias, self.env))
