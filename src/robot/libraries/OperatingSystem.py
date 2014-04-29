#  Copyright 2008-2014 Nokia Solutions and Networks
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
import codecs
import fnmatch
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import time

try:
    from robot.version import get_version
    from robot.api import logger
    from robot.utils import (ConnectionCache, seq2str, timestr_to_secs,
                             secs_to_timestr, plural_or_not, get_time, abspath,
                             secs_to_timestamp, parse_time, unic, decode_output,
                             get_env_var, set_env_var, del_env_var, get_env_vars,
                             decode_from_system)
    __version__ = get_version()
    PROCESSES = ConnectionCache('No active processes')
    del ConnectionCache, get_version

# Support for using this library without installed Robot Framework
except ImportError:
    from os.path import abspath
    from os import (getenv as get_env_var, putenv as set_env_var,
                    unsetenv as del_env_var, environ)
    __version__ = '<unknown>'
    get_env_vars = environ.copy
    logger = None
    seq2str = lambda items: ', '.join("'%s'" % item for item in items)
    timestr_to_secs = int
    plural_or_not = lambda count: '' if count == 1 else 's'
    secs_to_timestr = lambda secs: '%d second%s' % (secs, plural_or_not(secs))
    unic = unicode
    decode_output = decode_from_system = lambda string: string
    class _NotImplemented:
        def __getattr__(self, name):
            raise NotImplementedError('This usage requires Robot Framework '
                                      'to be installed.')
    get_time = secs_to_timestamp = parse_time = PROCESSES = _NotImplemented()


class OperatingSystem:
    """A test library providing keywords for OS related tasks.

    `OperatingSystem` is Robot Framework's standard library that
    enables various operating system related tasks to be performed in
    the system where Robot Framework is running. It can, among other
    things, execute commands (e.g. `Run`), create and remove files and
    directories (e.g. `Create File`, `Remove Directory`), check
    whether files or directories exists or contain something
    (e.g. `File Should Exist`, `Directory Should Be Empty`) and
    manipulate environment variables (e.g. `Set Environment Variable`).

    = Pattern matching =

    Some keywords allow their arguments to be specified as _glob patterns_
    where:
    | *        | matches anything, even an empty string |
    | ?        | matches any single character |
    | [chars]  | matches any character inside square brackets (e.g. '[abc]' matches either 'a', 'b' or 'c') |
    | [!chars] | matches any character not inside square brackets |

    Unless otherwise noted, matching is case-insensitive on
    case-insensitive operating systems such as Windows. Pattern
    matching is implemented using
    [http://docs.python.org/library/fnmatch.html|fnmatch module].

    = Path separators =

    All keywords expecting paths as arguments accept a forward slash
    (`/`) as a path separator regardless the operating system. Notice
    that this *does not work when the path is part of an argument*,
    like it often is with `Run` and `Start Process` keywords. In such
    cases the built-in variable `${/}` can be used to keep the test
    data platform independent.

    = Tilde expansion =

    Paths beginning with `~` or `~username` are expanded to the current or
    specified user's home directory, respectively. The resulting path is
    operating system dependent, but typically e.g. `~/robot` is expanded to
    `C:\\Users\\<user>\\robot` on Windows and `/home/<user>/robot` on Linuxes.

    Notice that the `~username` form does not work on Jython or on Windows
    python 2.5. Tilde expansion is a new feature in Robot Framework 2.8.

    = Process library =

    Process library replaces old process keywords (`Start Process` and
    `Switch Process`) from OperatingSystem library. These keywords in the
    OperatingSystem library might be deprecated in the future. This library is
    new in Robot Framework 2.8.

    = Example =

    |  *Setting*  |     *Value*     |
    | Library     | OperatingSystem |

    | *Variable*  |       *Value*         |
    | ${PATH}     | ${CURDIR}/example.txt |

    | *Test Case* |     *Action*      | *Argument* |    *Argument*        |
    | Example     | Create File       | ${PATH}    | Some text            |
    |             | File Should Exist | ${PATH}    |                      |
    |             | Copy File         | ${PATH}    | ~/file.txt           |
    |             | ${output} =       | Run | ${TEMPDIR}${/}script.py arg |
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def run(self, command):
        """Runs the given command in the system and returns the output.

        The execution status of the command *is not checked* by this
        keyword, and it must be done separately based on the returned
        output. If the execution return code is needed, either `Run
        And Return RC` or `Run And Return RC And Output` can be used.

        The standard error stream is automatically redirected to the standard
        output stream by adding `2>&1` after the executed command. This
        automatic redirection is done only when the executed command does not
        contain additional output redirections. You can thus freely forward
        the standard error somewhere else, for example, like
        `my_command 2>stderr.txt`.

        The returned output contains everything written into the standard
        output or error streams by the command (unless either of them
        is redirected explicitly). Many commands add an extra newline
        (`\\n`) after the output to make it easier to read in the
        console. To ease processing the returned output, this possible
        trailing newline is stripped by this keyword.

        Examples:
        | ${output} =        | Run       | ls -lhF /tmp |
        | Log                | ${output} |
        | ${result} =        | Run       | ${CURDIR}${/}tester.py arg1 arg2 |
        | Should Not Contain | ${result} | FAIL |
        | ${stdout} =        | Run       | /opt/script.sh 2>/tmp/stderr.txt |
        | Should Be Equal    | ${stdout} | TEST PASSED |
        | File Should Be Empty | /tmp/stderr.txt |
        """
        return self._run(command)[1]

    def run_and_return_rc(self, command):
        """Runs the given command in the system and returns the return code.

        The return code (RC) is returned as a positive integer in
        range from 0 to 255 as returned by the executed command. On
        some operating systems (notable Windows) original return codes
        can be something else, but this keyword always maps them to
        the 0-255 range. Since the RC is an integer, it must be
        checked e.g. with the keyword `Should Be Equal As Integers`
        instead of `Should Be Equal` (both are built-in keywords).

        Examples:
        | ${rc} = | Run and Return RC | ${CURDIR}${/}script.py arg |
        | Should Be Equal As Integers | ${rc} | 0 |
        | ${rc} = | Run and Return RC | /path/to/example.rb arg1 arg2 |
        | Should Be True | 0 < ${rc} < 42 |

        See `Run` and `Run And Return RC And Output` if you need to get the
        output of the executed command.
        """
        return self._run(command)[0]

    def run_and_return_rc_and_output(self, command):
        """Runs the given command in the system and returns the RC and output.

        The return code (RC) is returned similarly as with `Run And Return RC`
        and the output similarly as with `Run`.

        Examples:
        | ${rc} | ${output} =  | Run and Return RC and Output | ${CURDIR}${/}mytool |
        | Should Be Equal As Integers | ${rc}    | 0    |
        | Should Not Contain   | ${output}       | FAIL |
        | ${rc} | ${stdout} =  | Run and Return RC and Output | /opt/script.sh 2>/tmp/stderr.txt |
        | Should Be True       | ${rc} > 42      |
        | Should Be Equal      | ${stdout}       | TEST PASSED |
        | File Should Be Empty | /tmp/stderr.txt |
        """
        return self._run(command)

    def _run(self, command):
        process = _Process(command)
        self._info("Running command '%s'" % process)
        stdout = process.read()
        rc = process.close()
        return rc, stdout

    def start_process(self, command, stdin=None, alias=None):
        """It is recommended to use same keyword from Process library instead.

        Starts the given command as a background process.

        Starts the process in background and sets it as the active process.
        `Read Process Output` or `Stop Process` keywords affect this process
        unless `Switch Process` is used in between.

        If the command needs input through the standard input stream,
        it can be defined with the `stdin` argument.  It is not
        possible to give input to the command later. Possible command
        line arguments must be given as part of the command like
        '/tmp/script.sh arg1 arg2'.

        Returns the index of this process. Indexing starts from 1, and indices
        can be used to switch between processes using `Switch Process` keyword.
        `Stop All Processes` can be used to reset indexing.

        The optional `alias` is a name for this process that may be used with
        `Switch Process` instead of the returned index.

        The standard error stream is redirected to the standard input
        stream automatically. This is done for the same reasons as with `Run`
        keyword, but redirecting is done when the process is started and not
        by adding '2>&1' to the command.

        Example:
        | Start Process  | /path/longlasting.sh |
        | Do Something   |                      |
        | ${output} =    | Read Process Output  |
        | Should Contain | ${output}            | Expected text |
        | [Teardown]     | Stop All Processes   |
        """
        process = _Process2(command, stdin)
        self._info("Running command '%s'" % process)
        return PROCESSES.register(process, alias)

    def switch_process(self, index_or_alias):
        """It is recommended to use same keyword from Process library instead.

        Switches the active process to the specified process.

        New active process can be specified either using an index or an alias.
        Indices are return values from `Start Process` and aliases can be
        given to that keyword.

        Example:
        | Start Process  | /path/script.sh arg  | alias=1st process |
        | ${2nd} =       | Start Process        | /path/script2.sh |
        | Switch Process | 1st process          |
        | ${out1} =      | Read Process Output  |
        | Switch Process | ${2nd}               |
        | ${out2} =      | Read Process Output  |
        | Log Many       | 1st process: ${out1} | 2nd process: ${out1} |
        | [Teardown]     | Stop All Processes   |
        """
        PROCESSES.switch(index_or_alias)

    def read_process_output(self):
        """Waits for a process to finish and returns its output.

        This keyword waits for a process started with `Start Process` to end
        and then returns all output it has produced. The returned output
        contains everything the process has written into the standard output
        and error streams.

        There is no need to use `Stop Process` after using this keyword.
        Trying to read from an already stopped process fails.

        Note that although the process is finished, it still stays as the
        active process. Use `Switch Process` to switch the active process or
        `Stop All Processes` to reset the list of started processes.
        """
        output = PROCESSES.current.read()
        PROCESSES.current.close()
        return output

    def stop_process(self):
        """Closes the standard output stream of the process.

        This keyword does not actually stop the process nor even wait for it
        to terminate. Only thing it does is closing the standard output stream
        of the process. Depending on the process that may terminate it but
        that is not guaranteed. Use `Read Process Output` instead if you need
        to wait for the process to complete.

        This keyword operates the active process similarly as `Read Process
        Output`. Stopping an already stopped process is not an error.
        """
        PROCESSES.current.close()

    def stop_all_processes(self):
        """Closes the standard output of all the processes and resets the process list.

        Exactly like `Stop Process`, this keyword does not actually stop
        processes nor even wait for them to terminate.

        This keyword resets the indexing that `Start Process` uses. All aliases
        are also deleted. It does not matter have some of the processes
        already been closed or not.
        """
        PROCESSES.close_all()

    def get_file(self, path, encoding='UTF-8', encoding_errors='strict'):
        """Returns the contents of a specified file.

        This keyword reads the specified file and returns the contents.
        Line breaks in content are converted to platform independent form.
        See also `Get Binary File`.

        `encoding` defines the encoding of the file. By default the value is
        'UTF-8', which means that UTF-8 and ASCII-encoded files are read
        correctly.

        `encoding_errors` argument controls what to do if decoding some bytes
        fails. All values accepted by `decode` method in Python are valid, but
        in practice the following values are most useful:

        - `strict`: fail if characters cannot be decoded (default)
        - `ignore`: ignore characters that cannot be decoded
        - `replace`: replace characters that cannot be decoded with
          a replacement character

        `encoding_errors` argument is new in Robot Framework 2.8.5.
        """
        content = self.get_binary_file(path)
        return unicode(content, encoding, encoding_errors).replace('\r\n', '\n')

    def get_binary_file(self, path):
        """Returns the contents of a specified file.

        This keyword reads the specified file and returns the contents as is.
        See also `Get File`.

        New in Robot Framework 2.5.5.
        """
        path = self._absnorm(path)
        self._link("Getting file '%s'", path)
        with open(path, 'rb') as f:
            return f.read()

    def grep_file(self, path, pattern, encoding='UTF-8', encoding_errors='strict'):
        """Returns the lines of the specified file that match the `pattern`.

        This keyword reads a file from the file system using the defined
        `path`, `encoding` and `encoding_errors` similarly as `Get File`. A
        difference is that only the lines that match the given `pattern` are
        returned. Lines are returned as a single string catenated back together
        with newlines and the number of matched lines is automatically logged.
        Possible trailing newline is never returned.

        A line matches if it contains the `pattern` anywhere in it and
        it *does not need to match the pattern fully*. The pattern
        matching syntax is explained in `introduction`, and in this
        case matching is case-sensitive.

        Examples:
        | ${errors} = | Grep File | /var/log/myapp.log | ERROR |
        | ${ret} = | Grep File | ${CURDIR}/file.txt | [Ww]ildc??d ex*ple |

        If more complex pattern matching is needed, it is possible to use
        `Get File` in combination with String library keywords like `Get
        Lines Matching Regexp`.

        `encoding_errors` argument is new in Robot Framework 2.8.5.
        """
        pattern = '*%s*' % pattern
        path = self._absnorm(path)
        lines = []
        total_lines = 0
        self._link("Reading file '%s'", path)
        with codecs.open(path, encoding=encoding, errors=encoding_errors) as f:
            for line in f.readlines():
                total_lines += 1
                line = line.rstrip('\r\n')
                if fnmatch.fnmatchcase(line, pattern):
                    lines.append(line)
            self._info('%d out of %d lines matched' % (len(lines), total_lines))
            return '\n'.join(lines)

    def log_file(self, path, encoding='UTF-8', encoding_errors='strict'):
        """Wrapper for `Get File` that also logs the returned file.

        The file is logged with the INFO level. If you want something else,
        just use `Get File` and the built-in keyword `Log` with the desired
        level.

        `encoding_errors` argument is new in Robot Framework 2.8.5.
        """
        content = self.get_file(path, encoding, encoding_errors)
        self._info(content)
        return content

    # File and directory existence

    def should_exist(self, path, msg=None):
        """Fails unless the given path (file or directory) exists.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        if not glob.glob(path):
            self._fail(msg, "Path '%s' does not match any file or directory" % path)
        self._link("Path '%s' exists", path)

    def should_not_exist(self, path, msg=None):
        """Fails if the given path (file or directory) exists.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        matches = glob.glob(path)
        if not matches:
            self._link("Path '%s' does not exist", path)
            return
        if not msg:
            if self._is_pattern_path(path):
                matches.sort()
                msg = "Path '%s' matches %s" % (path, seq2str(matches))
            else:
                msg = "Path '%s' exists" % path
        raise AssertionError(msg)

    def file_should_exist(self, path, msg=None):
        """Fails unless the given `path` points to an existing file.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        matches = [p for p in glob.glob(path) if os.path.isfile(p)]
        if not matches:
            self._fail(msg, "Path '%s' does not match any file" % path)
        self._link("File '%s' exists", path)

    def file_should_not_exist(self, path, msg=None):
        """Fails if the given path points to an existing file.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        matches = [p for p in glob.glob(path) if os.path.isfile(p)]
        if not matches:
            self._link("File '%s' does not exist", path)
            return
        if not msg:
            if self._is_pattern_path(path):
                matches.sort()
                name = len(matches) == 1 and 'file' or 'files'
                msg = "Path '%s' matches %s %s" % (path, name, seq2str(matches))
            else:
                msg = "File '%s' exists" % path
        raise AssertionError(msg)

    def directory_should_exist(self, path, msg=None):
        """Fails unless the given path points to an existing directory.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        matches = [p for p in glob.glob(path) if os.path.isdir(p)]
        if not matches:
            self._fail(msg, "Path '%s' does not match any directory" % path)
        self._link("Directory '%s' exists", path)

    def directory_should_not_exist(self, path, msg=None):
        """Fails if the given path points to an existing file.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        matches = [p for p in glob.glob(path) if os.path.isdir(p)]
        if not matches:
            self._link("Directory '%s' does not exist", path)
            return
        if not msg:
            if self._is_pattern_path(path):
                matches.sort()
                name = len(matches) == 1 and 'directory' or 'directories'
                msg = "Path '%s' matches %s %s" % (path, name, seq2str(matches))
            else:
                msg = "Directory '%s' exists" % path
        raise AssertionError(msg)

    def _is_pattern_path(self, path):
        return '*' in path or '?' in path or ('[' in path and ']' in path)

    # Waiting file/dir to appear/disappear

    def wait_until_removed(self, path, timeout='1 minute'):
        """Waits until the given file or directory is removed.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        If the path is a pattern, the keyword waits until all matching
        items are removed.

        The optional `timeout` can be used to control the maximum time of
        waiting. The timeout is given as a timeout string, e.g. in a format
        '15 seconds', '1min 10s' or just '10'. The time string format is
        described in an appendix of Robot Framework User Guide.

        If the timeout is negative, the keyword is never timed-out. The keyword
        returns immediately, if the path does not exist in the first place.
        """
        path = self._absnorm(path)
        timeout = timestr_to_secs(timeout)
        maxtime = time.time() + timeout
        while glob.glob(path):
            time.sleep(0.1)
            if timeout >= 0 and time.time() > maxtime:
                raise AssertionError("'%s' was not removed in %s"
                                     % (path, secs_to_timestr(timeout)))
        self._link("'%s' was removed", path)

    def wait_until_created(self, path, timeout='1 minute'):
        """Waits until the given file or directory is created.

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        If the path is a pattern, the keyword returns when an item matching
        it is created.

        The optional `timeout` can be used to control the maximum time of
        waiting. The timeout is given as a timeout string, e.g. in a format
        '15 seconds', '1min 10s' or just '10'. The time string format is
        described in an appendix of Robot Framework User Guide.

        If the timeout is negative, the keyword is never timed-out. The keyword
        returns immediately, if the path already exists.
        """
        path = self._absnorm(path)
        timeout = timestr_to_secs(timeout)
        maxtime = time.time() + timeout
        while not glob.glob(path):
            time.sleep(0.1)
            if timeout >= 0 and time.time() > maxtime:
                raise AssertionError("'%s' was not created in %s"
                                     % (path, secs_to_timestr(timeout)))
        self._link("'%s' was created", path)

    # Dir/file empty

    def directory_should_be_empty(self, path, msg=None):
        """Fails unless the specified directory is empty.

        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        items = self._list_dir(path)
        if items:
            if not msg:
                msg = "Directory '%s' is not empty. Contents: %s" \
                        % (path, seq2str(items, lastsep=', '))
            raise AssertionError(msg)
        self._link("Directory '%s' is empty.", path)

    def directory_should_not_be_empty(self, path, msg=None):
        """Fails if the specified directory is empty.

        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        count = len(self._list_dir(path))
        if count == 0:
            self._fail(msg, "Directory '%s' is empty." % path)
        plural = plural_or_not(count)
        self._link("Directory '%%s' contains %d item%s." % (count, plural),
                   path)

    def file_should_be_empty(self, path, msg=None):
        """Fails unless the specified file is empty.

        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        if not os.path.isfile(path):
            raise AssertionError("File '%s' does not exist" % path)
        size = os.stat(path).st_size
        if size > 0:
            self._fail(msg, "File '%s' is not empty. Size: %d bytes" % (path, size))
        self._link("File '%s' is empty", path)

    def file_should_not_be_empty(self, path, msg=None):
        """Fails if the specified directory is empty.

        The default error message can be overridden with the `msg` argument.
        """
        path = self._absnorm(path)
        if not os.path.isfile(path):
            raise AssertionError("File '%s' does not exist" % path)
        size = os.stat(path).st_size
        if size == 0:
            self._fail(msg, "File '%s' is empty." % path)
        self._link("File '%%s' contains %d bytes" % size, path)

    # Creating and removing files and directory

    def create_file(self, path, content='', encoding='UTF-8'):
        """Creates a file with the given content and encoding.

        If the directory where to create file does not exist it, and possible
        intermediate missing directories, are created.

        Examples:
        | Create File | ${dir}/example.txt | Hello, world!      |         |
        | Create File | ${path}            | Hyv\\xe4 esimerkki | latin-1 |

        Use `Append To File` if you want to append to an existing file
        and `Create Binary File` if you need to write bytes without encoding.
        `File Should Not Exist` can be used to avoid overwriting existing
        files.
        """
        path = self._write_to_file(path, content, encoding)
        self._link("Created file '%s'", path)

    def create_binary_file(self, path, content):
        """Creates a binary file with the given content.

        If content is given as a Unicode string, it is first converted to bytes
        character by character. All characters with ordinal below 256 can be
        used and are converted to bytes with same values.

        Byte strings, and possible other types, are written to the file as is.

        If the directory where to create file does not exist it, and possible
        intermediate missing directories, are created.

        Examples:
        | Create Binary File | ${dir}/example.png | ${image content}     |
        | Create Binary File | ${path}            | \\x01\\x00\\xe4\\x00 |

        Use `Create File` if you want to create a text file using a certain
        encoding. `File Should Not Exist` can be used to avoid overwriting
        existing files.

        New in Robot Framework 2.8.5.
        """
        if isinstance(content, unicode):
            content = ''.join(chr(ord(c)) for c in content)
        path = self._write_to_file(path, content)
        self._link("Created binary file '%s'", path)

    def append_to_file(self, path, content, encoding='UTF-8'):
        """Appends the given contend to the specified file.

        If the file does not exists, this keyword works exactly the same
        way as `Create File`.
        """
        path = self._write_to_file(path, content, encoding, mode='a')
        self._link("Appended to file '%s'", path)

    def _write_to_file(self, path, content, encoding=None, mode='w'):
        path = self._absnorm(path)
        parent = os.path.dirname(path)
        if not os.path.exists(parent):
            os.makedirs(parent)
        if encoding:
            content = content.encode(encoding)
        with open(path, mode+'b') as f:
            f.write(content)
        return path

    def remove_file(self, path):
        """Removes a file with the given path.

        Passes if the file does not exist, but fails if the path does
        not point to a regular file (e.g. it points to a directory).

        The path can be given as an exact path or as a glob pattern.
        The pattern matching syntax is explained in `introduction`.
        If the path is a pattern, all files matching it are removed.
        """
        path = self._absnorm(path)
        matches = glob.glob(path)
        if not matches:
            self._link("File '%s' does not exist", path)
        for match in matches:
            if not os.path.isfile(match):
                raise RuntimeError("Path '%s' is not a file" % match)
            os.remove(match)
            self._link("Removed file '%s'", match)

    def remove_files(self, *paths):
        """Uses `Remove File` to remove multiple files one-by-one.

        Example:
        | Remove Files | ${TEMPDIR}${/}foo.txt | ${TEMPDIR}${/}bar.txt | ${TEMPDIR}${/}zap.txt |
        """
        for path in paths:
            self.remove_file(path)

    def empty_directory(self, path):
        """Deletes all the content (incl. subdirectories) from the given directory."""
        path = self._absnorm(path)
        items = [os.path.join(path, item) for item in self._list_dir(path)]
        for item in items:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
        self._link("Emptied directory '%s'", path)

    def create_directory(self, path):
        """Creates the specified directory.

        Also possible intermediate directories are created. Passes if the
        directory already exists, and fails if the path points to a regular
        file.
        """
        path = self._absnorm(path)
        if os.path.isdir(path):
            self._link("Directory '%s' already exists", path )
            return
        if os.path.exists(path):
            raise RuntimeError("Path '%s' already exists but is not a directory" % path)
        os.makedirs(path)
        self._link("Created directory '%s'", path)

    def remove_directory(self, path, recursive=False):
        """Removes the directory pointed to by the given `path`.

        If the second argument `recursive` is set to any non-empty string,
        the directory is removed recursively. Otherwise removing fails if
        the directory is not empty.

        If the directory pointed to by the `path` does not exist, the keyword
        passes, but it fails, if the `path` points to a file.
        """
        path = self._absnorm(path)
        if not os.path.exists(path):
            self._link("Directory '%s' does not exist", path)
            return
        if os.path.isfile(path):
            raise RuntimeError("Path '%s' is not a directory" % path)
        if recursive:
            shutil.rmtree(path)
        else:
            msg = "Directory '%s' is not empty." % path
            self.directory_should_be_empty(path, msg)
            os.rmdir(path)
        self._link("Removed directory '%s'", path)

    # Moving and copying files and directories

    def copy_file(self, source, destination):
        """Copies the source file into the destination.

        Source must be an existing file. Starting from Robot Framework 2.8.4,
        it can be given as a glob pattern (see `Pattern matching`) that matches
        exactly one file. How the destination is interpreted is explained below.

        1) If the destination is an existing file, the source file is copied
        over it.

        2) If the destination is an existing directory, the source file is
        copied into it. A possible file with the same name as the source is
        overwritten.

        3) If the destination does not exist and it ends with a path
        separator ('/' or '\\'), it is considered a directory. That
        directory is created and a source file copied into it.
        Possible missing intermediate directories are also created.

        4) If the destination does not exist and it does not end with a path
        separator, it is considered a file. If the path to the file does not
        exist, it is created.

        See also `Copy Files`, `Move File`, and `Move Files`.
        """
        source, destination = self._copy_file(source, destination)
        self._link("Copied file from '%s' to '%s'", source, destination)

    def move_file(self, source, destination):
        """Moves the source file into the destination.

        Arguments have exactly same semantics as with `Copy File` keyword.

        If the source and destination are on the same filesystem, rename
        operation is used. Otherwise file is copied to the destination
        filesystem and then removed from the original filesystem.

        See also `Move Files`, `Copy File`, and `Copy Files`.
        """
        source, destination, _ = self._prepare_for_move_or_copy(source, destination)
        shutil.move(source, destination)
        self._link("Moved file from '%s' to '%s'", source, destination)

    def copy_files(self, *sources_and_destination):
        """Copies specified files to the target directory.

        Source files can be given as exact paths and as glob patterns (see
        `Pattern matching`). At least one source must be given, but it is
        not an error if it is a pattern that does not match anything.

        Last argument must be the destination directory. If the destination
        does not exist, it will be created.

        Examples:
        | Copy Files | ${dir}/file1.txt  | ${dir}/file2.txt | ${dir2} |
        | Copy Files | ${dir}/file-*.txt | ${dir2}          |         |

        See also `Copy File`, `Move File`, and `Move Files`.

        New in Robot Framework 2.8.4.
        """
        source_files, dest_dir = self._parse_sources_and_destination(sources_and_destination)
        for source in source_files:
            self.copy_file(source, dest_dir)

    def move_files(self, *sources_and_destination):
        """Moves specified files to the target directory.

        Arguments have exactly same semantics as with `Copy Files` keyword.

        See also `Move File`, `Copy File`, and `Copy Files`.

        New in Robot Framework 2.8.4.
        """
        source_files, dest_dir = self._parse_sources_and_destination(sources_and_destination)
        for source in source_files:
            self.move_file(source, dest_dir)

    def _parse_sources_and_destination(self, items):
        if len(items) < 2:
            raise RuntimeError("Must contain destination and at least one source")
        sources, destination = items[:-1], items[-1]
        self._ensure_destination_directory(destination)
        return self._glob_files(sources), destination

    def _normalize_dest(self, dest):
        dest = dest.replace('/', os.sep)
        dest_is_dir = dest.endswith(os.sep) or os.path.isdir(dest)
        dest = self._absnorm(dest)
        return dest, dest_is_dir

    def _ensure_destination_directory(self, destination):
        destination, _ = self._normalize_dest(destination)
        if not os.path.exists(destination):
            os.makedirs(destination)
        elif not os.path.isdir(destination):
            raise RuntimeError("Destination '%s' exists and is not a directory" % destination)

    def _glob_files(self, patterns):
        files = []
        for pattern in patterns:
            files.extend(glob.glob(self._absnorm(pattern)))
        return files

    def _prepare_for_move_or_copy(self, source, dest):
        source, dest, dest_is_dir = self._normalize_source_and_dest(source, dest)
        self._verify_that_source_is_a_file(source)
        parent = self._ensure_directory_exists(dest, dest_is_dir)
        self._ensure_dest_file_does_not_exist(source, dest, dest_is_dir)
        return source, dest, parent

    def _ensure_dest_file_does_not_exist(self, source, dest, dest_is_dir):
        if dest_is_dir:
            dest = os.path.join(dest, os.path.basename(source))
        if os.path.isfile(dest):
            os.remove(dest)

    def _copy_file(self, source, dest):
        source, dest, parent = self._prepare_for_move_or_copy(source, dest)
        return self._atomic_copy(source, dest, parent)

    def _normalize_source_and_dest(self, source, dest):
        sources = self._glob_files([source])
        if len(sources) > 1:
            raise RuntimeError("Multiple matches with source pattern '%s'" % source)
        source = sources[0] if sources else source
        dest, dest_is_dir = self._normalize_dest(dest)
        return source, dest, dest_is_dir

    def _verify_that_source_is_a_file(self, source):
        if not os.path.exists(source):
            raise RuntimeError("Source file '%s' does not exist" % source)
        if not os.path.isfile(source):
            raise RuntimeError("Source file '%s' is not a regular file" % source)

    def _ensure_directory_exists(self, dest, dest_is_dir):
        parent = dest if dest_is_dir else os.path.dirname(dest)
        if not os.path.exists(dest) and not os.path.exists(parent):
            os.makedirs(parent)
        return parent

    def _atomic_copy(self, source, destination, destination_parent):
        # This method tries to ensure that a file copy operation will not fail if the destination file is removed during
        # copy operation.
        # This has been an issue for at least some of the users that had a mechanism that polled and removed
        # the destination - their test cases sometimes failed because the copy file failed.
        # This is done by first copying the source to a temporary directory on the same drive as the destination is
        # and then moving (that is almost always in every platform an atomic operation) that temporary file to
        # the destination.
        # See http://code.google.com/p/robotframework/issues/detail?id=1502 for details
        temp_directory = tempfile.mkdtemp(dir=destination_parent) # Temporary directory can be atomically created
        temp_file = os.path.join(temp_directory, os.path.basename(source))
        shutil.copy(source, temp_file)
        shutil.move(temp_file, destination)
        os.rmdir(temp_directory)
        return source, destination

    def copy_directory(self, source, destination):
        """Copies the source directory into the destination.

        If the destination exists, the source is copied under it. Otherwise
        the destination directory and the possible missing intermediate
        directories are created.
        """
        source, destination = self._copy_dir(source, destination)
        self._link("Copied directory from '%s' to '%s'", source, destination)

    def move_directory(self, source, destination):
        """Moves the source directory into a destination.

        Uses `Copy Directory` keyword internally, and `source` and
        `destination` arguments have exactly same semantics as with
        that keyword.
        """
        source, destination = self._prepare_copy_or_move_dir(source, destination)
        shutil.move(source, destination)
        self._link("Moved directory from '%s' to '%s'", source, destination)

    def _copy_dir(self, source, dest):
        source, dest = self._prepare_copy_or_move_dir(source, dest)
        shutil.copytree(source, dest)
        return source, dest

    def _prepare_copy_or_move_dir(self, source, dest):
        source = self._absnorm(source)
        dest = self._absnorm(dest)
        if not os.path.exists(source):
            raise RuntimeError("Source directory '%s' does not exist" % source)
        if not os.path.isdir(source):
            raise RuntimeError("Source directory '%s' is not a directory" % source)
        if os.path.exists(dest) and not os.path.isdir(dest):
            raise RuntimeError("Destination '%s' exists but is not a directory" % dest)
        if os.path.exists(dest):
            base = os.path.basename(source)
            dest = os.path.join(dest, base)
        else:
            parent = os.path.dirname(dest)
            if not os.path.exists(parent):
                os.makedirs(parent)
        return source, dest

    # Environment Variables

    def get_environment_variable(self, name, default=None):
        """Returns the value of an environment variable with the given name.

        If no such environment variable is set, returns the default value, if
        given. Otherwise fails the test case.

        Starting from Robot Framework 2.7, returned variables are automatically
        decoded to Unicode using the system encoding.

        Note that you can also access environment variables directly using
        the variable syntax `%{ENV_VAR_NAME}`.
        """
        value = get_env_var(name, default)
        if value is None:
            raise RuntimeError("Environment variable '%s' does not exist" % name)
        return value

    def set_environment_variable(self, name, value):
        """Sets an environment variable to a specified value.

        Values are converted to strings automatically. Starting from Robot
        Framework 2.7, set variables are automatically encoded using the system
        encoding.
        """
        set_env_var(name, value)
        self._info("Environment variable '%s' set to value '%s'" % (name, value))

    def append_to_environment_variable(self, name, *values, **config):
        """Appends given `values` to environment variable `name`.

        If the environment variable already exists, values are added after it,
        and otherwise a new environment variable is created.

        Values are, by default, joined together using the operating system
        path separator (';' on Windows, ':' elsewhere). This can be changed
        by giving a separator after the values like `separator=value`. No
        other configuration parameters are accepted.

        Examples (assuming `NAME` and `NAME2` do not exist initially):
        | Append To Environment Variable | NAME     | first  |       |
        | Should Be Equal                | %{NAME}  | first  |       |
        | Append To Environment Variable | NAME     | second | third |
        | Should Be Equal                | %{NAME}  | first${:}second${:}third |
        | Append To Environment Variable | NAME2    | first  | separator=-     |
        | Should Be Equal                | %{NAME2} | first  |                 |
        | Append To Environment Variable | NAME2    | second | separator=-     |
        | Should Be Equal                | %{NAME2} | first-second             |

        New in Robot Framework 2.8.4.
        """
        sentinel = object()
        initial = self.get_environment_variable(name, sentinel)
        if initial is not sentinel:
            values = (initial,) + values
        separator = config.pop('separator', os.pathsep)
        if config:
            config = ['='.join(i) for i in sorted(config.items())]
            raise RuntimeError('Configuration %s not accepted.'
                               % seq2str(config, lastsep=' or '))
        self.set_environment_variable(name, separator.join(values))

    def remove_environment_variable(self, *names):
        """Deletes the specified environment variable.

        Does nothing if the environment variable is not set.

        Starting from Robot Framework 2.7, it is possible to remove multiple
        variables by passing them to this keyword as separate arguments.
        """
        for name in names:
            value = del_env_var(name)
            if value:
                self._info("Environment variable '%s' deleted" % name)
            else:
                self._info("Environment variable '%s' does not exist" % name)

    def environment_variable_should_be_set(self, name, msg=None):
        """Fails if the specified environment variable is not set.

        The default error message can be overridden with the `msg` argument.
        """
        value = get_env_var(name)
        if not value:
            self._fail(msg, "Environment variable '%s' is not set" % name)
        self._info("Environment variable '%s' is set to '%s'" % (name, value))

    def environment_variable_should_not_be_set(self, name, msg=None):
        """Fails if the specified environment variable is set.

        The default error message can be overridden with the `msg` argument.
        """
        value = get_env_var(name)
        if value:
            self._fail(msg, "Environment variable '%s' is set to '%s'" % (name, value))
        self._info("Environment variable '%s' is not set" % name)

    def get_environment_variables(self):
        """Returns currently available environment variables as a dictionary.

        Both keys and values are decoded to Unicode using the system encoding.
        Altering the returned dictionary has no effect on the actual environment
        variables.

        New in Robot Framework 2.7.
        """
        return get_env_vars()

    def log_environment_variables(self, level='INFO'):
        """Logs all environment variables using the given log level.

        Environment variables are also returned the same way as with
        `Get Environment Variables` keyword.

        New in Robot Framework 2.7.
        """
        vars = get_env_vars()
        for name, value in sorted(vars.items(), key=lambda item: item[0].lower()):
            self._log('%s = %s' % (name, value), level)
        return vars

    # Path

    def join_path(self, base, *parts):
        """Joins the given path part(s) to the given base path.

        The path separator ('/' or '\\') is inserted when needed and
        the possible absolute paths handled as expected. The resulted
        path is also normalized.

        Examples:
        | ${path} = | Join Path | my        | path  |
        | ${p2} =   | Join Path | my/       | path/ |
        | ${p3} =   | Join Path | my        | path  | my | file.txt |
        | ${p4} =   | Join Path | my        | /path |
        | ${p5} =   | Join Path | /my/path/ | ..    | path2 |
        =>
        - ${path} = 'my/path'
        - ${p2} = 'my/path'
        - ${p3} = 'my/path/my/file.txt'
        - ${p4} = '/path'
        - ${p5} = '/my/path2'
        """
        base = base.replace('/', os.sep)
        parts = [p.replace('/', os.sep) for p in parts]
        return self.normalize_path(os.path.join(base, *parts))

    def join_paths(self, base, *paths):
        """Joins given paths with base and returns resulted paths.

        See `Join Path` for more information.

        Examples:
        | @{p1} = | Join Path | base     | example       | other |          |
        | @{p2} = | Join Path | /my/base | /example      | other |          |
        | @{p3} = | Join Path | my/base  | example/path/ | other | one/more |
        =>
        - @{p1} = ['base/example', 'base/other']
        - @{p2} = ['/example', '/my/base/other']
        - @{p3} = ['my/base/example/path', 'my/base/other', 'my/base/one/more']
        """
        return [self.join_path(base, path) for path in paths]

    def normalize_path(self, path):
        """Normalizes the given path.

        Examples:
        | ${path} = | Normalize Path | abc        |
        | ${p2} =   | Normalize Path | abc/       |
        | ${p3} =   | Normalize Path | abc/../def |
        | ${p4} =   | Normalize Path | abc/./def  |
        | ${p5} =   | Normalize Path | abc//def   |
        =>
        - ${path} = 'abc'
        - ${p2} = 'abc'
        - ${p3} = 'def'
        - ${p4} = 'abc/def'
        - ${p5} = 'abc/def'
        """
        path = os.path.normpath(os.path.expanduser(path.replace('/', os.sep)))
        return path or '.'

    def split_path(self, path):
        """Splits the given path from the last path separator ('/' or '\\').

        The given path is first normalized (e.g. a possible trailing
        path separator is removed, special directories '..' and '.'
        removed). The parts that are split are returned as separate
        components.

        Examples:
        | ${path1} | ${dir} =  | Split Path | abc/def         |
        | ${path2} | ${file} = | Split Path | abc/def/ghi.txt |
        | ${path3} | ${d2}  =  | Split Path | abc/../def/ghi/ |
        =>
        - ${path1} = 'abc' & ${dir} = 'def'
        - ${path2} = 'abc/def' & ${file} = 'ghi.txt'
        - ${path3} = 'def' & ${d2} = 'ghi'
        """
        return os.path.split(self.normalize_path(path))

    def split_extension(self, path):
        """Splits the extension from the given path.

        The given path is first normalized (e.g. possible trailing
        path separators removed, special directories '..' and '.'
        removed). The base path and extension are returned as separate
        components so that the dot used as an extension separator is
        removed. If the path contains no extension, an empty string is
        returned for it. Possible leading and trailing dots in the file
        name are never considered to be extension separators.

        Examples:
        | ${path} | ${ext} = | Split Extension | file.extension    |
        | ${p2}   | ${e2} =  | Split Extension | path/file.ext     |
        | ${p3}   | ${e3} =  | Split Extension | path/file         |
        | ${p4}   | ${e4} =  | Split Extension | p1/../p2/file.ext |
        | ${p5}   | ${e5} =  | Split Extension | path/.file.ext    |
        | ${p6}   | ${e6} =  | Split Extension | path/.file        |
        =>
        - ${path} = 'file' & ${ext} = 'extension'
        - ${p2} = 'path/file' & ${e2} = 'ext'
        - ${p3} = 'path/file' & ${e3} = ''
        - ${p4} = 'p2/file' & ${e4} = 'ext'
        - ${p5} = 'path/.file' & ${e5} = 'ext'
        - ${p6} = 'path/.file' & ${e6} = ''
        """
        path = self.normalize_path(path)
        basename = os.path.basename(path)
        if basename.startswith('.' * basename.count('.')):
            return path, ''
        if path.endswith('.'):
            path2 = path.rstrip('.')
            trailing_dots = '.' * (len(path) - len(path2))
            path = path2
        else:
            trailing_dots = ''
        basepath, ext = os.path.splitext(path)
        if ext.startswith('.'):
            ext = ext[1:]
        if ext:
            ext += trailing_dots
        else:
            basepath += trailing_dots
        return basepath, ext

    # Misc

    def get_modified_time(self, path, format='timestamp'):
        """Returns the last modification time of a file or directory.

        How time is returned is determined based on the given `format`
        string as follows. Note that all checks are case-insensitive.
        Returned time is also automatically logged.

        1) If `format` contains the word 'epoch', the time is returned
           in seconds after the UNIX epoch. The return value is always
           an integer.

        2) If `format` contains any of the words 'year', 'month',
           'day', 'hour', 'min' or 'sec', only the selected parts are
           returned. The order of the returned parts is always the one
           in the previous sentence and the order of the words in
           `format` is not significant. The parts are returned as
           zero-padded strings (e.g. May -> '05').

        3) Otherwise, and by default, the time is returned as a
           timestamp string in the format '2006-02-24 15:08:31'.

        Examples (when the modified time of the ${CURDIR} is
        2006-03-29 15:06:21):
        | ${time} = | Get Modified Time | ${CURDIR} |
        | ${secs} = | Get Modified Time | ${CURDIR} | epoch |
        | ${year} = | Get Modified Time | ${CURDIR} | return year |
        | ${y} | ${d} = | Get Modified Time | ${CURDIR} | year,day |
        | @{time} = | Get Modified Time | ${CURDIR} | year,month,day,hour,min,sec |
        =>
        - ${time} = '2006-03-29 15:06:21'
        - ${secs} = 1143637581
        - ${year} = '2006'
        - ${y} = '2006' & ${d} = '29'
        - @{time} = ['2006', '03', '29', '15', '06', '21']
        """
        path = self._absnorm(path)
        if not os.path.exists(path):
            raise RuntimeError("Getting modified time of '%s' failed: "
                               "Path does not exist" % path)
        mtime = get_time(format, os.stat(path).st_mtime)
        self._link("Last modified time of '%%s' is %s" % mtime, path)
        return mtime

    def set_modified_time(self, path, mtime):
        """Sets the file modification and access times.

        Changes the modification and access times of the given file to
        the value determined by `mtime`. The time can be given in
        different formats described below. Note that all checks
        involving strings are case-insensitive.

        1) If `mtime` is a number, or a string that can be converted
           to a number, it is interpreted as seconds since the UNIX
           epoch (1970-01-01 00:00:00 UTC). This documentation was
           originally written about 1177654467 seconds after the epoch.

        2) If `mtime` is a timestamp, that time will be used. Valid
           timestamp formats are 'YYYY-MM-DD hh:mm:ss' and 'YYYYMMDD hhmmss'.

        3) If `mtime` is equal to 'NOW', the current local time is used.
           This time is got using Python's 'time.time()' function.

        4) If `mtime` is equal to 'UTC', the current time in
           [http://en.wikipedia.org/wiki/Coordinated_Universal_Time|UTC]
           is used. This time is got using 'time.time() + time.altzone'
           in Python.

        5) If `mtime` is in the format like 'NOW - 1 day' or 'UTC + 1
           hour 30 min', the current local/UTC time plus/minus the time
           specified with the time string is used. The time string format
           is described in an appendix of Robot Framework User Guide.

        Examples:
        | Set Modified Time | /path/file | 1177654467         | # Time given as epoch seconds |
        | Set Modified Time | /path/file | 2007-04-27 9:14:27 | # Time given as a timestamp   |
        | Set Modified Time | /path/file | NOW                | # The local time of execution |
        | Set Modified Time | /path/file | NOW - 1 day        | # 1 day subtracted from the local time |
        | Set Modified Time | /path/file | UTC + 1h 2min 3s   | # 1h 2min 3s added to the UTC time |

        Support for UTC time is a new feature in Robot Framework 2.7.5.
        """
        path = self._absnorm(path)
        try:
            if not os.path.exists(path):
                raise ValueError('File does not exist')
            if not os.path.isfile(path):
                raise ValueError('Modified time can only be set to regular files')
            mtime = parse_time(mtime)
        except ValueError, err:
            raise RuntimeError("Setting modified time of '%s' failed: %s"
                               % (path, unicode(err)))
        os.utime(path, (mtime, mtime))
        time.sleep(0.1)  # Give os some time to really set these times
        tstamp = secs_to_timestamp(mtime, ('-',' ',':'))
        self._link("Set modified time of '%%s' to %s" % tstamp, path)

    def get_file_size(self, path):
        """Returns and logs file size as an integer in bytes"""
        path = self._absnorm(path)
        if not os.path.isfile(path):
            raise RuntimeError("File '%s' does not exist." % path)
        size = os.stat(path).st_size
        plural = plural_or_not(size)
        self._link("Size of file '%%s' is %d byte%s" % (size, plural), path)
        return size

    def list_directory(self, path, pattern=None, absolute=False):
        """Returns and logs items in a directory, optionally filtered with `pattern`.

        File and directory names are returned in case-sensitive alphabetical
        order, e.g. ['A Name', 'Second', 'a lower case name', 'one more'].
        Implicit directories '.' and '..' are not returned. The returned items
        are automatically logged.

        By default, the file and directory names are returned relative to the
        given path (e.g. 'file.txt'). If you want them be returned in the
        absolute format (e.g. '/home/robot/file.txt'), set the `absolute`
        argument to any non-empty string.

        If `pattern` is given, only items matching it are returned. The pattern
        matching syntax is explained in `introduction`, and in this case
        matching is case-sensitive.

        Examples (using also other `List Directory` variants):
        | @{items} = | List Directory           | ${TEMPDIR} |
        | @{files} = | List Files In Directory  | /tmp | *.txt | absolute |
        | ${count} = | Count Files In Directory | ${CURDIR} | ??? |
        """
        items = self._list_dir(path, pattern, absolute)
        self._info('%d item%s:\n%s' % (len(items), plural_or_not(items), '\n'.join(items)))
        return items

    def list_files_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only files."""
        files = self._list_files_in_dir(path, pattern, absolute)
        self._info('%d file%s:\n%s' % (len(files), plural_or_not(files), '\n'.join(files)))
        return files

    def list_directories_in_directory(self, path, pattern=None, absolute=False):
        """A wrapper for `List Directory` that returns only directories."""
        dirs = self._list_dirs_in_dir(path, pattern, absolute)
        self._info('%d director%s:\n%s' % (len(dirs), 'y' if len(dirs) == 1 else 'ies', '\n'.join(dirs)))
        return dirs

    def count_items_in_directory(self, path, pattern=None):
        """Returns and logs the number of all items in the given directory.

        The argument `pattern` has the same semantics as in the `List Directory`
        keyword. The count is returned as an integer, so it must be checked e.g.
        with the built-in keyword `Should Be Equal As Integers`.
        """
        count = len(self._list_dir(path, pattern))
        self._info("%s item%s." % (count, plural_or_not(count)))
        return count

    def count_files_in_directory(self, path, pattern=None):
        """A wrapper for `Count Items In Directory` returning only file count."""
        count = len(self._list_files_in_dir(path, pattern))
        self._info("%s file%s." % (count, plural_or_not(count)))
        return count

    def count_directories_in_directory(self, path, pattern=None):
        """A wrapper for `Count Items In Directory` returning only directory count."""
        count = len(self._list_dirs_in_dir(path, pattern))
        self._info("%s director%s." % (count, 'y' if count == 1 else 'ies'))
        return count

    def _list_dir(self, path, pattern=None, absolute=False):
        path = self._absnorm(path)
        self._link("Listing contents of directory '%s'.", path)
        if not os.path.isdir(path):
            raise RuntimeError("Directory '%s' does not exist" % path)
        # result is already unicode but unic also handles NFC normalization
        items = sorted(unic(item) for item in os.listdir(path))
        if pattern:
            items = [i for i in items if fnmatch.fnmatchcase(i, pattern)]
        if absolute:
            path = os.path.normpath(path)
            items = [os.path.join(path,item) for item in items]
        return items

    def _list_files_in_dir(self, path, pattern=None, absolute=False):
        return [item for item in self._list_dir(path, pattern, absolute)
                if os.path.isfile(os.path.join(path, item))]

    def _list_dirs_in_dir(self, path, pattern=None, absolute=False):
        return [item for item in self._list_dir(path, pattern, absolute)
                if os.path.isdir(os.path.join(path, item))]

    def touch(self, path):
        """Emulates the UNIX touch command.

        Creates a file, if it does not exist. Otherwise changes its access and
        modification times to the current time.

        Fails if used with the directories or the parent directory of the given
        file does not exist.
        """
        path = self._absnorm(path)
        if os.path.isdir(path):
            raise RuntimeError("Cannot touch '%s' because it is a directory" % path)
        if not os.path.exists(os.path.dirname(path)):
            raise RuntimeError("Cannot touch '%s' because its parent directory "
                            "does not exist" % path)
        if os.path.exists(path):
            mtime = round(time.time())
            os.utime(path, (mtime, mtime))
            self._link("Touched existing file '%s'", path)
        else:
            open(path, 'w').close()
            self._link("Touched new file '%s'", path)

    def _absnorm(self, path):
        path = self.normalize_path(path)
        try:
            return abspath(path)
        except ValueError:  # http://ironpython.codeplex.com/workitem/29489
            return path

    def _fail(self, error, default):
        raise AssertionError(error or default)

    def _info(self, msg):
        self._log(msg, 'INFO')

    def _link(self, msg, *paths):
        paths = tuple('<a href="file://%s">%s</a>' % (p, p) for p in paths)
        self._log(msg % paths, 'HTML')

    def _warn(self, msg):
        self._log(msg, 'WARN')

    def _log(self, msg, level):
        if logger:
            logger.write(msg, level)
        else:
            print '*%s* %s' % (level, msg)


class _Process:

    def __init__(self, command):
        self._command = self._process_command(command)
        self._process = os.popen(self._command)

    def __str__(self):
        return self._command

    def read(self):
        return self._process_output(self._process.read())

    def close(self):
        try:
            rc = self._process.close()
        except IOError:  # Has occurred sometimes in Windows
            return 255
        if rc is None:
            return 0
        # In Windows (Python and Jython) return code is value returned by
        # command (can be almost anything)
        # In other OS:
        #   In Jython return code can be between '-255' - '255'
        #   In Python return code must be converted with 'rc >> 8' and it is
        #   between 0-255 after conversion
        if os.sep == '\\' or sys.platform.startswith('java'):
            return rc % 256
        return rc >> 8

    def _process_command(self, command):
        if '>' not in command:
            if command.endswith('&'):
                command = command[:-1] + ' 2>&1 &'
            else:
                command += ' 2>&1'
        return self._encode_to_file_system(command)

    def _encode_to_file_system(self, string):
        enc = sys.getfilesystemencoding()
        return string.encode(enc) if enc else string

    def _process_output(self, stdout):
        stdout = stdout.replace('\r\n', '\n') # http://bugs.jython.org/issue1566
        if stdout.endswith('\n'):
            stdout = stdout[:-1]
        return decode_output(stdout, force=True)


class _Process2(_Process):

    def __init__(self, command, input_):
        self._command = self._process_command(command)
        p = subprocess.Popen(self._command, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             close_fds=os.sep=='/')
        stdin, self.stdout = p.stdin, p.stdout
        if input_:
            stdin.write(input_)
        stdin.close()
        self.closed = False

    def read(self):
        if self.closed:
            raise RuntimeError('Cannot read from a closed process')
        return self._process_output(self.stdout.read())

    def close(self):
        if not self.closed:
            self.stdout.close()
            self.closed = True
