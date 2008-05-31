#  Copyright 2008 Nokia Siemens Networks Oyj
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


import os
import re
import shutil
import time
import fnmatch
import glob

from robot import utils
from robot.errors import DataError
import robot.output
import BuiltIn


builtin = BuiltIn.BuiltIn()
PROCESSES = utils.ConnectionCache('No active processes')


class OperatingSystem:
    
    """This test library enables multiple operating system related tasks."""

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    
    def run(self, command, return_mode='stdout'):
        """Runs given command in system and returns return code and/or stdout.
        
        'return_mode' defines how return code (rc) and standard output (stdout)
        are returned as explained below. All checks are case insensitive.
        * If it contains word 'rc' and either word 'stdout' or 'output', both
          the rc and stdout are returned.
        * Otherwise, if it contains word 'rc', only the rc is returned.
        * Otherwise, and by default, only the stdout is returned.
                
        The rc is returned as an integer. It must thus be checked e.g. with 
        keyword 'Should Be Equal As Integers' instead of 'Should Be Equal' (both
        are built-in keywords). Return codes are positive integers in range
        from 0 to 255 as returned by the command (if the command returns some
        other value the system maps it into this range).
        
        The returned output contains everything written into the stdout by the
        command. Many commands add an extra newline (\\n) after the output to
        make reading it easier in the console. To ease processing the returned
        output Robot strips this possible newline.
        
        Possible standard error (stderr) from the executed command is NOT
        captured by this keyword or other parts of Robot. If catching stderr is
        important it must be redirected into stdout or some file. The former 
        can be achieved, both in Windows and unixes, with syntax 
        'my_command 2>&1' and the latter with 'my_command 2>stderr.txt'.
        
        Examples:
        | ${output} = | Run | ls -lhF /tmp | 
        | Log | ${output} |
        | ${rc} = | Run | ${CURDIR}${/}script.py  | Return RC  |
        | Should Be Equal As Integers | ${rc} | 0 |
        | ${rc} | ${out} = | Run | /opt/script.py 2>&1 | RC,Output |
        | Fail Unless | ${rc} > 0 |
        | Contains | ${out} | TEST PASSED |
        """
        self._info("Running command '%s'" % command)
        if utils.is_jython:
            # Jython's os.popen doesn't handle unicode as explained in
            # http://jython.org/bugs/1735774
            command = str(command)
        process = os.popen(command)
        stdout = process.read()
        if stdout.endswith('\n'):
            stdout = stdout[:-1]
        try:
            rc = process.close()   # May raise IOError at least in Windows
        except:
            rc = -1   # -1 is eventually turned into 255
        if rc is None: 
            rc = 0
        # In Windows (Python and Jython) return code is value returned by 
        # command (can be almost anything)
        # In other OS:
        #   In Jython return code can be between '-255' - '255'
        #   In Python return code must be converted with 'rc >> 8' and it is
        #   between 0-255 after conversion 
        if utils.is_windows or utils.is_jython:
            rc = rc % 256
        else:
            rc = rc >> 8
        if utils.contains(return_mode, 'rc'):
            if utils.contains_any(return_mode, ['stdout','output']):
                return rc, stdout
            return rc
        return stdout
    
    def run_and_return_rc(self, command):
        """Wrapper for 'Run' keyword that returns only the return code.
        
        Following two examples are equivalent but the latter is easier to
        understand and thus recommended.
        
        | ${rc} = | Run               | my_command | RC |
        | ${rc} = | Run and Return RC | my_command |    |
        """
        return self.run(command, 'RC')
    
    def run_and_return_rc_and_output(self, command):
        """Wrapper for 'Run' keyword that returns the return code and output.
        
        Following two examples are equivalent but the latter is easier to
        understand and thus recommended.
        
        | ${rc} | ${output} = | Run                  | my_command | RC, Output |
        | ${rc} | ${output} = | Run and Return RC and Output | my_command |    |
        
        Note that similarly as normal 'Run' this keyword only returns the 
        standard output and not the standard error. Use either format
        'my_command 2>/tmp/stderr.txt' to redirect the stderr into a specific
        file or 'my_command 2>&1' to return it along with the stdout.
        """
        return self.run(command, 'RC,Output')
    
    def start_process(self, command, stdin='', alias=None):
        """Starts given command as a background process.
        
        Starts the process in the background and sets this process as the 
        current process so that following calls of keywords 'Read Process Output'
        and 'Stop Process' affect this process unless keyword 'Switch Process' is
        used in between.
        
        If the command needs input, it can be defined with 'stdin' argument. It 
        is not possible give input to the command later.
        
        Returns the index of this process. Indexing starts from 1, and it can 
        be used to switch between processes with 'Switch Process' keyword. To 
        end all processes and reset indexing, 'Stop All Processes' keyword 
        must be used.
        
        Optional 'alias' is a name for this process that may be used with 
        'Switch Process' instead of the returned index.
        
        See Robot documentation on ConnectionCache for full details on aliases
        and process switching.
        """
        self._info("Running command '%s'" % command)
        process = _Process(command, stdin)
        return PROCESSES.register(process, alias)
    
    def switch_process(self, index_or_alias):
        """Switch the current process to process found with 'index_or_alias'.
        
        Index is the return value of 'Start Process' keyword and alias may have 
        been defined to it.
        """
        PROCESSES.switch(index_or_alias)
    
    def read_process_output(self, mode='stdout'):
        """Waits for the process to finish and returns its output.
        
        'mode' defines which outputs are returned. If it contains 'stdout', 
        standard output is returned. If it contains 'stderr' standard error is 
        returned. If it contains 'stderr' and 'stdout' or 'both', standard 
        output and standard error are returned.
        
        If mode contains only 'stdout', but there are contents on stderr, this
        keyword will fail.
        
        Note that although the process is finished, it is not removed from the 
        process list. Trying to read from a stopped process will nevertheless 
        fail. To reset the process list (and indices and aliases) 
        'Stop All Processes' must be used. 
        
        See 'Start Process' and 'Switch Process' for more information.
        """
        process = PROCESSES.get_current()
        if (utils.contains(mode, 'stdout') and utils.contains(mode, 'stderr')) \
                or utils.contains(mode, 'both'):
            return process.read_stdout_and_stderr()
        if utils.contains(mode, 'stderr'):
            return process.read_stderr()
        return process.read_stdout()
        
    def stop_process(self):
        """Stops the current process without reading from it.
        
        Stopping a process will not remove it from the process list. To reset 
        the process list (and indices and aliases) 'Stop All Processes' must be 
        used.
        
        See 'Start Process' and 'Switch Process' for more information.
        """
        PROCESSES.get_current().close()
        
    def stop_all_processes(self):
        """Stops all the processes and removes them from the process list.
        
        Resets the indexing that 'Start Process' uses. All aliases are also 
        deleted.
        """
        PROCESSES.close_all()
    
    def get_file(self, path, encoding='UTF-8'):
        """Return contents of specified file.
        
        This keyword reads the specified file and returns the contents. 
        'encoding' defines the encoding of the file. By default the value is 
        'UTF-8', which means that UTF-8 and ascii encoded files are
        read correctly.
        """
        self._info("Getting file '%s'" % path)
        f = open(path, 'rb')
        content = f.read()
        f.close()
        return unicode(content, encoding).replace('\r\n', '\n')
    
    # TODO: Remove in 1.9
    def get_file_with_encoding(self, path, encoding='UTF-8'):
        """Deprecated. Will be removed in Robot 1.9
        
        This keyword reads the specified file and returns the contents. 
        'encoding' defines the encoding of the file. By default the value is 
        'UTF-8', which means that UTF-8 and ascii encoded files are
        read correctly.
        """
        robot.output.SYSLOG.warn("Keyword 'OperatingSystem.Get File With Encoding' "
                                 "is deprecated and will be removed in Robot 1.9. "
                                 "Please use 'OperatingSystem.Get File' instead.") 
        return self.get_file(path, encoding)

    def grep_file(self, path, pattern, pattern_type='literal string', 
                 encoding='UTF-8'):
        """Returns contents of specified file grepped using 'pattern'.
        
        This keyword reads the specified file and returns only lines matching 
        the 'pattern'. 'encoding' defines the encoding of the file. By default 
        the value is 'UTF-8', which means that UTF-8 and ascii encoded files are
        read correctly.
        
        'pattern_type' defines how the given pattern is interpreted as explained
        below. 'pattern_type' argument is case insensitive and may contain other
        text. For example 'regexp', 'REGEXP' and 'Pattern is a regexp' are all 
        considered equal.
        
        - If 'pattern_type' contains either string 'simple' or 'glob' the 
          'pattern' is considered a simple pattern and lines returned only if 
          they match it. (1) 
        - If 'pattern_type' contains either string 'regular expression' or
          'regexp' the 'pattern' is considered a regular expression and only 
          lines matching it returned. (2)
        - If 'pattern_type' contains string 'case insensitive' the 'pattern' is 
          considered a literal string and lines returned if they contain the 
          string regardless of the case.
        - Otherwise the pattern is considered a literal string and lines
          returned if they contain the string exactly. This is the default.
        
        1) Simple pattern matching is similar as matching files in a shell and 
        it is always case-sensitive. In the pattern '*' matches to anything 
        and '?' matches to any single character. 
  
        2) Regular expression check is done using Python 're' module which has 
        a pattern syntax derived from Perl and thus also very similar to the 
        one in Java. See following documents from more details about regexps
        in general and their Python implementation in particular.
        
        're' Module Documentation: http://docs.python.org/lib/module-re.html
        Regular Expression HOWTO: http://www.amk.ca/python/howto/regex/
        
        Note that if you want to use flags (e.g. re.IGNORECASE) you have to
        embed them into the pattern (e.g. '(?i)pattern'). Note also that 
        backslash is an escape character in Robot test data and possible
        backslaches in patterns must thus be escaped with another backslash
        (e.g. '\\\\d\\\\w+').
        """
        content = self.get_file(path, encoding)
        content = builtin.grep(content, pattern, pattern_type)
        self._info('Matching file content:\n' + content)
        return content
    
    def log_file(self, path, encoding='UTF-8'):
        """Wrapper for 'Get File' that also logs the returned file.
        
        File is logged with INFO level, if you want something else just use
        'Get File' and built-in keyword 'Log' with desired level. 
        """
        content = self.get_file(path, encoding)
        self._info('File content:\n' + content)
        return content
        
    # File and directory existence
    
    def should_exist(self, path, msg=None):
        """Fails unless given path (file or directory) exists.
        
        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = glob.glob(path)
        if len(matches) == 0:
            self._fail(msg, "Path '%s' does not match any file or directory" % path)
        self._info("Path '%s' exists" % path)
        
    def should_not_exist(self, path, msg=None):
        """Fails if given path (file or directory) exists.

        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = glob.glob(path)
        if len(matches) > 0:
            if msg is None:
                if self._is_pattern_path(path):
                    matches.sort()
                    msg = "Path '%s' matches %s" % (path, utils.seq2str(matches))
                else:
                    msg = "Path '%s' exists" % path
            raise AssertionError(msg)
        self._info("Path '%s' does not exist" % path)
        
    def file_should_exist(self, path, msg=None):
        """Fails unless given path points to an existing file.
        
        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = [ p for p in glob.glob(path) if os.path.isfile(p) ]
        if len(matches) == 0:
            self._fail(msg, "Path '%s' does not match any file" % path)
        self._info("File '%s' exists" % path)

    def file_should_not_exist(self, path, msg=None):
        """Fails if given path points to an existing file.
        
        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = [ p for p in glob.glob(path) if os.path.isfile(p) ]
        if len(matches) > 0:
            if msg is None:
                if self._is_pattern_path(path):
                    matches.sort()
                    name = len(matches) == 1 and 'file' or 'files'
                    msg = "Path '%s' matches %s %s" % (path, name,
                                                             utils.seq2str(matches))
                else:
                    msg = "File '%s' exists" % path
            raise AssertionError(msg)
        self._info("File '%s' does not exist" % path)

    def directory_should_exist(self, path, msg=None):
        """Fails unless given path points to an existing directory.
        
        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = [ p for p in glob.glob(path) if os.path.isdir(p) ]
        if len(matches) == 0:
            self._fail(msg, "Path '%s' does not match any directory" % path)
        self._info("Directory '%s' exists" % path)

    def directory_should_not_exist(self, path, msg=None):
        """Fails if given path points to an existing file.
        
        Path can be given as an exact path or as a pattern where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Default error message can be overridden with 'msg' argument.
        """
        matches = [ p for p in glob.glob(path) if os.path.isdir(p) ]
        if len(matches) > 0:
            if msg is None:
                if self._is_pattern_path(path):
                    matches.sort()
                    name = len(matches) == 1 and 'directory' or 'directories'
                    msg = "Path '%s' matches %s %s" % (path, name, utils.seq2str(matches))
                else:
                    msg = "Directory '%s' exists" % path
            raise AssertionError(msg)
        self._info("Directory '%s' does not exist" % path)
        
    def _is_pattern_path(self, path):
        return path.count('*') > 0 or path.count('?') > 0 \
                or (path.count('[') > 0 and path.count(']') > 0)


    # Waiting file/dir to appear/disappear

    def wait_until_removed(self, path, timeout='1 minute'):
        """Waits until the given file or directory is removed.
        
        Path can be given as an exact path or as a pattern where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        If path is a pattern, the keyword waits until all matching items are
        removed.
             
        Optional 'timeout' can be used to control how long to wait in maximum.
        Timeout is given as a timeout string e.g. in format '15 min' or '1min 10s'.
        The time string format is described in Robot documentation TimeSyntax.

        If the timeout is negative the keyword never timeouts. The keyword returns
        immediatelly if the file/directory does not exist in the first place. 
        """
        matches = glob.glob(path)
        if len(matches) == 0:
            self._info("No items found matching to '%s' found" % path)
        else:
            self._info('Waiting for following items to be removed: %s' % ', '.join(matches) )
        timeout = utils.timestr_to_secs(timeout)
        starttime = time.time()
        while os.path.exists(path):
            time.sleep(0.1)
            if timeout >= 0 and time.time() > starttime + timeout:
                raise AssertionError("Item '%s' was not removed in %s" 
                                     % (path, utils.secs_to_timestr(timeout)))
    
    def wait_until_created(self, path, timeout='1 minute'):
        """Waits until the given file or directory is created.

        Path can be given as an exact path or as a pattern where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        If path is a pattern, the keyword returns when an item matching to 
        pattern is creted.

        Optional 'timeout' can be used to control how long to wait in maximum.
        Timeout is given as a timeout string e.g. in format '15 min' or '1min 10s'.
        The time string format is described in Robot documentation TimeSyntax.
        
        If the timeout is negative the keyword never timeouts. The keyword returns
        immediatelly if the file/directory already exist. 
        """
        timeout = utils.timestr_to_secs(timeout)
        starttime = time.time()
        matches = glob.glob(path)
        while len(matches) == 0:
            time.sleep(0.1)
            matches = glob.glob(path)
            if timeout >= 0 and time.time() > starttime + timeout:
                raise AssertionError("Item '%s' was not created in %s" 
                                     % (path, utils.secs_to_timestr(timeout)))


    # Dir/file empty

    def directory_should_be_empty(self, path, msg=None):
        """Fails unless the specified directory is empty.
        
        Default error message can be overridden with 'msg' argument.
        """
        if not os.path.isdir(path):
            raise AssertionError("Directory '%s' does not exist" % path)
        entries = self._list_dir(path)
        if len(entries) > 0:
            if msg is None:
                msg = "Directory '%s' is not empty. Contents: %s" \
                        % (path, utils.seq2str(entries, lastsep=', '))
            raise AssertionError(msg)
        self._info("Directory '%s' is empty." % path)
    
    def directory_should_not_be_empty(self, path, msg=None):
        """Fails if the specified directory is empty.
        
        Default error message can be overridden with 'msg' argument.
        """
        if not os.path.isdir(path):
            raise AssertionError("Directory '%s' does not exist" % path)
        count = len(self._list_dir(path))
        if count == 0:
            self._fail(msg, "Directory '%s' is empty." % path)
        plural = utils.plural_or_not(count)
        self._info("Directory '%s' contains %d item%s." % (path, count, plural)) 

    def file_should_be_empty(self, path, msg=None):
        """Fails unless the specified file is empty.
        
        Default error message can be overridden with 'msg' argument.
        """
        if not os.path.isfile(path):
            raise AssertionError("File '%s' does not exist" % path)
        size = self.get_file_size(path)
        if size > 0:
            self._fail(msg, "File '%s' is not empty. Size: %d bytes" % (path, size))
        self._info("File '%s' is empty" % path)
    
    def file_should_not_be_empty(self, path, msg=None):
        """Fails if the specified directory is empty.
        
        Default error message can be overridden with 'msg' argument.
        """
        if not os.path.isfile(path):
            raise AssertionError("File '%s' does not exist" % path)
        size = self.get_file_size(path)
        if size == 0:
            self._fail(msg, "File '%s' is empty." % path)
        self._info("File '%s' contains %d bytes" % (path, size))
    
    
    # Creating and removing files and directory

    def create_file(self, path, content='', mode='overwrite'):
        """Creates file to given path with given content.
        
        If mode contains any of the strings 'False', 'No', "Don't" (case 
        insensitive so e.g. "Do not" works also) keyword fails if file alreaydy
        exists and file is not overwritten. If it contains word 'Append'
        (case insensitive) content is appended and otherwise file is
        overwritten.
        
        If the directory where to create file does not exist it, and possible
        intermediate missing directories, are created.
        """
        if utils.contains_any(mode, ['False','No',"Don't"]):
            self.file_should_not_exist(path)
        open_mode = utils.contains(mode, 'Append') and 'a' or 'w'
        parent = os.path.dirname(os.path.abspath(os.path.normpath(path)))
        if not os.path.exists(parent):
            os.makedirs(parent)
        f = open(path, open_mode)
        f.write(content)
        f.close()
        self._info("Created file '%s'" % path)
        
    def remove_file(self, path):
        """Removes file with given path.
        
        Passes if file does not exist but fails if path does not point to
        a regular file (e.g. it points to a directory).
        
        Path can be given as an exact path or as a patter where         
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        """
        matches = glob.glob(path)
        if len(matches) == 0:
            self._info("File '%s' does not exist" % path)
        for match in matches:
            if not os.path.isfile(match):
                raise DataError("Path '%s' is not a file" % match)
            os.remove(match)
            self._info("Removed file '%s'" % match)
        
    def remove_files(self, *paths):
        """Uses 'Remove File' to remove multiple files one-by-one."""
        for path in paths:
            self.remove_file(path)
        
    def empty_directory(self, path):
        """Deletes all the content (incl. subdirs) from the given directory."""
        items = [ os.path.join(path, item) for item in self._list_dir(path) ]
        for item in items:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
        self._info("Emptied directory '%s'" % path)

    def create_directory(self, path):
        """Creates directory, and all intermediate ones, with given path.
        
        Passes if directory does not exist and fails if path does not point to
        a regular file (e.g. it points to a directory).
        """
        if os.path.isdir(path):
            self._info("Directory '%s' already exists" % path )
            return
        if os.path.exists(path):
            raise DataError("Path '%s' already exists but is not a directory" % path)
        os.makedirs(path)
        self._info("Created directory '%s'" % path)
    
    # TODO: Remove synonym    
    create_dir = create_directory 
        
    def remove_directory(self, path, recursive='no'):
        """Removes directory pointed by given 'path' optionally recursively.
        
        If second argument 'recursive' contains any of the words 'yes', 'true'
        or 'recursive' (case insensitive) all directory contents are removed
        also. Otherwise removing fails if directory is not empty.
        
        If directory pointed by the 'path' does not exist keyword passes but it
        fails if the 'path' points to a file.
        """
        if not os.path.exists(path):
            self._info("Directory '%s' does not exist" % path)
            return
        if os.path.isfile(path):
            raise DataError("Path '%s' is not a directory" % path)
        if self._is_recursive(recursive):
            shutil.rmtree(path)
        else:
            msg = "Directory '%s' is not empty." % path
            self.directory_should_be_empty(path, msg)
            os.rmdir(path)
        self._info("Removed directory '%s'" % path)
            
    def _is_recursive(self, recursive):
        return utils.contains_any(recursive, ['yes','true','recursive'])
            
    # Moving and copying files and directories
            
    def copy_file(self, source, destination):
        """Copies source file into new destination.
        
        1) If the destination is an existing file, the source file is copied
        over it.
        2) If the destination is an existing directory, the source file is
        copied into it. Possible file with same name is overwritten.
        3) If the destination does not exist and it ends with path separator 
        ('/' in unixes, '\\' in Windows), it is considered a directory. That 
        directory is created and source file copied into it. Possible missing
        intermediate directories are also created.
        4) If the destination does not exist and it does not end with path
        separator, it is considered a file. If the path to the file does not
        exist it is created.
        """
        self._copy_file(source, destination)
        self._info("Copied file from '%s' to '%s'" % (source, destination))
        
    def _copy_file(self, source, destination):
        if not os.path.exists(source):
            raise DataError("Source file '%s' does not exist" % source)
        if not os.path.isfile(source):
            raise DataError("Source file '%s' is not a regular file" % source)
        if not os.path.exists(destination):
            if destination.endswith(os.sep):
                parent = destination
            else:
                parent = os.path.dirname(os.path.normpath(destination))
            if not os.path.exists(parent):
                os.makedirs(parent)
        shutil.copy(source, destination)

    def copy_directory(self, source, destination):
        """Copies source directory into destination.
        
        If destination exists source is copied under it, otherwise destination
        directory and possible missing intermediate directories are created.
        """
        self._copy_dir(source, destination)
        self._info("Copied directory from '%s' to '%s'" % (source, destination))
        
    def _copy_dir(self, source, destination):
        if not os.path.exists(source):
            raise DataError("Source directory '%s' does not exist" % source)
        if not os.path.isdir(source):
            raise DataError("Source directory '%s' is not a directory" % source)
        if os.path.exists(destination) and not os.path.isdir(destination):
            raise DataError("Destination '%s' exists but is not a directory" 
                               % destination)
        if os.path.exists(destination):
            base = os.path.basename(os.path.normpath(source))
            destination = os.path.join(destination, base)
        else:
            parent = os.path.dirname(os.path.normpath(destination))
            if not os.path.exists(parent):
                os.makedirs(parent)
        shutil.copytree(source, destination)

    def move_file(self, source, destination):
        """Moves source file into new destination.
        
        Destination may be file or a directory and in the latter case file's
        original basename is kept. If the destination file exists it is
        overwritten. Missing intermediate directories are NOT created.
        """
        self._copy_file(source, destination)
        os.remove(source)
        self._info("Moved file from '%s' to '%s'" % (source, destination))

    def move_directory(self, source, destination):
        """Moves source directory into destination.
        
        If destination exists source is moved under it, otherwise destination
        directory and possible missing intermediate directories are created.
        """
        self._copy_dir(source, destination)
        shutil.rmtree(source)
        self._info("Moved directory from '%s' to '%s'" % (source, destination))


    # Environment Variables

    def get_environment_variable(self, name, default=None):
        """Returns the value of an environment variable with given name.
        
        If no such environment variable is set returns the default value if 
        given and otherwise fails the test case.
        
        Note that you can also access environment variables directly using
        variable syntax %{ENV_VAR_NAME}.
        """
        ret = os.environ.get(name, default)
        if ret is None:
            raise DataError("Environment variable '%s' does not exist" % name)
        return ret
        
    def set_environment_variable(self, name, value):
        """Sets environment variable to specified value"""
        os.environ[name] = value
        self._info("Environment variable '%s' set to value '%s'" % (name, value))

    def remove_environment_variable(self, name):
        """Deletes specified environment variable.
        
        Does nothing if the environment variable is not set.
        """
        if os.environ.has_key(name):
            del os.environ[name]
            self._info("Environment variable '%s' deleted" % name)
        else:
            self._info("Environment variable '%s' does not exist" % name)
    
    def environment_variable_should_be_set(self, name, msg=None):
        """Fails if the specified environment variable is not set.
        
        Default error message can be overridden with 'msg' argument.
        """
        try:
            value = os.environ[name]
        except KeyError:
            self._fail(msg, "Environment variable '%s' is not set" % name)
        else:
            self._info("Environment variable '%s' is set to '%s'" % (name, value))
            
    def environment_variable_should_not_be_set(self, name, msg=None):
        """Fails if the specified environment variable is set.
        
        Default error message can be overridden with 'msg' argument.
        """
        try:
            value = os.environ[name]
        except KeyError:
            self._info("Environment variable '%s' is not set" % name)
        else:
            self._fail(msg, "Environment variable '%s' is set to '%s'" % (name, value))

    
    # Path
         
    def join_path(self, base, *parts):
        """Joins the given path part(s) to the given base path.
        
        Path separator ('/' or '\\') is inserted when needed and possible
        absolute paths handled as expected. Resulted path is also normalized.
        
        Examples (assuming unix environment):
        | ${path} = | Join Path | my        | path  |
        | ${p2} =   | Join Path | my/       | path/ |
        | ${p3} =   | Join Path | my        | path  | my | file.txt |
        | ${p4} =   | Join Path | my        | /path |
        | ${p5} =   | Join Path | /my/path/ | ..    | path2 |
        =>
        ${path} = 'my/path'
        ${p2} = 'my/path'
        ${p3} = 'my/path/my/file.txt'
        ${p4} = '/path'
        ${p5} = '/my/path2'        
        """
        return os.path.normpath(os.path.join(base, *parts))
    
    def join_paths(self, base, *paths):
        """ Joins given paths with base and returns resulted paths.
        
        Examples (assuming unix environment):
        | @{p1} = | Join Path | base     | example       | other |          |
        | @{p2} = | Join Path | /my/base | /example      | other |          |
        | @{p3} = | Join Path | my/base  | example/path/ | other | one/more |
        =>
        @{p1} = [ 'base/example', 'base/other' ]
        @{p2} = [ '/example', '/my/base/other' ]
        @{p3} = [ 'my/base/example/path', 'my/base/other', 'my/base/one/more' ]
        """
        return [ self.join_path(base, path) for path in paths ]
        
    def normalize_path(self, path):
        """Normalizes the given path.
        
        Examples (assuming unix environment):
        | ${path} = | Normalize Path | abc        |
        | ${p2} =   | Normalize Path | abc/       |
        | ${p3} =   | Normalize Path | abc/../def |
        | ${p4} =   | Normalize Path | abc/./def  |
        | ${p5} =   | Normalize Path | abc//def   |
        =>
        ${path} = 'abc'
        ${p2} = 'abc'
        ${p3} = 'def'
        ${p4} = 'abc/def'
        ${p5} = 'abc/def'        
        """
        ret = os.path.normpath(path)
        if ret == '': return '.'
        return ret
        
    def split_path(self, path):
        """Splits the given path from the last path separator ('/' or '\\').
        
        Given path is first normalized (e.g. possible trailing path separator
        removed, special directories '..' and '.' removed). Splitted parts are
        returned as separate components.
        
        Examples (assuming unix environment):
        | ${path1} | ${dir} =  | Split Path | abc/def         |
        | ${path2} | ${file} = | Split Path | abc/def/ghi.txt |        
        | ${path3} | ${d2}  =  | Split Path | abc/../def/ghi/ |
        =>
        ${path1} = 'abc', ${dir} = 'def'
        ${path2} = 'abc/def', ${file} = 'ghi.txt'
        ${path3} = 'def', ${d2} = 'ghi'
        """
        return os.path.split(self.normalize_path(path))
    
    def split_extension(self, path):
        """Splits extension from the given path.
        
        Given path is first normalized (e.g. possible trailing path separator
        removed, special directories '..' and '.' removed). Splitted parts are
        returned as separate components. If path contains no extension an empty
        string is returned for it.
        
        Examples (assuming unix environment):
        | ${path} | ${ext} = | Split Extension | file.extension    |
        | ${p2}   | ${e2} =  | Split Extension | path/file.ext     |
        | ${p3}   | ${e3} =  | Split Extension | path/file         |
        | ${p4}   | ${e4} =  | Split Extension | p1/../p2/file.ext |
        =>
        ${path} = 'file', ${ext} = 'extension'
        ${p2} = 'path/file', ${e2} = 'ext'
        ${p3} = 'path/file', ${e3} = ''
        ${p4} = 'p2/file', ${e4} = 'ext'
        """
        base, ext = os.path.splitext(self.normalize_path(path))
        if len(ext) > 0 and ext[0] == '.':
            ext = ext[1:]
        return base, ext


    # Misc
    
    def get_modified_time(self, path, format='timestamp'):
        """Return the last modification time of a file or directory.
        
        How time is returned is deternined based on the given 'format' string as
        follows. Note that all checks are case insensitive.
        
        - If 'format' contains word 'epoch' the time is returned in seconds 
          after the unix epoch. Return value is always an integer.
        - If 'format' contains any of the words 'year', 'month', 'day', 'hour',
          'min' or 'sec' only selected parts are returned. The order of the
          returned parts is always the one in previous sentence and order of
          words in 'format' is not significant. Parts are returned as zero
          padded strings (e.g. May -> '05').
        - Otherwise (and by default) the time is returned as a timestamp string 
          in format '2006-02-24 15:08:31'
        
        Examples (when modified time of the ${CURDIR} is 2006-03-29 15:06:21):
        | ${time} = | Get Modified Time | ${CURDIR} |
        | ${secs} = | Get Modified Time | ${CURDIR} | epoch |
        | ${year} = | Get Modified Time | ${CURDIR} | return year |
        | ${y} | ${d} = | Get Modified Time | ${CURDIR} | year,day |
        | @{time} = | Get Modified Time | ${CURDIR} | year,month,day,hour,min,sec |
        =>
        ${time} = '2006-03-29 15:06:21'
        ${secs} = 1143637581
        ${year} = '2006'
        ${y} = '2006', ${d} = '29'
        @{time} = [ '2006', '03', '29', '15', '06', '21' ]
        """
        if not os.path.exists(path):
            raise DataError("Getting modified time of '%s' failed: "
                            "Path does not exist" % path)
        return utils.get_time(format, os.stat(path).st_mtime)

    def set_modified_time(self, path, mtime):
        """Sets the modified time of file.
        
        Changes the modified and access times of given file to value determined
        by 'mtime'. There are four different ways to give 'mtime'.
        
        1) If 'mtime' is a floating point number, it will be interpreted as 
        seconds since epoch (Jan 1, 1970 0:00:00). This documentation is written
        about 1177654467 seconds since epoch.
        
        2) If 'mtime' is a valid timestamp, that time will be used.
        Valid timestamp formats are 'YYYY-MM-DD hh:mm:ss' and 'YYYYMMDD hhmmss'. 
        
        3) If 'mtime' is equal to 'NOW' (case insensitive) current time is used.

        4) If 'mtime' is in format 'NOW - 1 day' or 'NOW + 1 hour 30 min' 
        current time plus/minus the time specified with time string is used. 
        The time string format is described in Robot documentation TimeSyntax.
        
        Examples:
        | Set Modified Time | /path/file | 1177654467         | #(2007-04-27 9:14:27) |
        | Set Modified Time | /path/file | 2007-04-27 9:14:27 |
        | Set Modified Time | /path/file | NOW                | # The time of execution |
        | Set Modified Time | /path/file | NOW - 1d           | # 1 day subtraced from NOW |
        | Set Modified Time | /path/file | NOW + 1h 2min 3s   | # 1h 2min 3s added to NOW |
        """
        try:
            if not os.path.exists(path):
                raise DataError('File does not exist')
            if not os.path.isfile(path):
                raise DataError('Modified time can only be set to regular files')
            mtime = self._parse_modified_time(mtime)
        except:
            raise DataError("Setting modified time of '%s' failed: %s"
                            % (path, utils.get_error_message()))
        os.utime(path, (mtime, mtime))
        time.sleep(0.1)  # Give os some time to really set these times
        tstamp = utils.secs_to_timestamp(mtime, ('-',' ',':'))
        self._info("Set modified time of '%s' to %s" % (path, tstamp))
        
    def _parse_modified_time(self, mtime):
        orig_time = mtime
        try:
            mtime = round(float(mtime))
            if mtime < 0:
                raise DataError("Epoch time must be positive (got %d)" % mtime)
            return mtime
        except ValueError:
            pass
        try:
            return utils.timestamp_to_secs(mtime, (' ', ':', '-', '.'))
        except DataError:
            pass
        mtime = utils.normalize(mtime)
        now = round(time.time())
        if mtime == 'now':
            return now
        if mtime.startswith('now'):
            if mtime[3] == '+':
                return now + utils.timestr_to_secs(mtime[4:])
            if mtime[3] == '-':
                return now - utils.timestr_to_secs(mtime[4:])
        raise DataError("Invalid time format '%s'" % orig_time)

    def get_file_size(self, path):
        """Returns file size as an integer in bytes"""
        # TODO: Add an option to return size in kilos, megas or gigas
        return os.stat(path).st_size
    
    def list_directory(self, path, pattern=None, pattern_type='simple', 
                 absolute=False):
        """Returns items from the given directory optionally filtered with 'pattern'.
                
        File and directory names are returned in case-sensitive alphabetical 
        order e.g. like ['A Name', 'Second', 'a lower case name', 'one more'].
        Implicit directories '.' and '..' are not returned. Returned items are
        automatically logged.
        
        By default file and directory names are returned relative to the given 
        path (e.g. 'file.txt'). If you want them be returned in absolute format 
        (e.g. '/home/robot/file.txt') set 'absolute' argument value to 'True', 
        'Yes' or 'absolute' (case insensitive).
                
        If no 'pattern' is given all item names are returned. If 'pattern' is
        given only names matching it are returned. 'pattern_type' defines how
        the given pattern is interpreted as explained below.
        
        - If 'pattern_type' contains a string 'simple' (case insensitive) the
          'pattern' is considered a simple pattern and items returned only if
          they match it. This is the default. (1) 
        - If 'pattern_type' contains either string 'regular expression' or
          'regexp' (case insensitive) the 'pattern' is considered a regular
          expression and only items matching it returned. (2)
        - Otherwise the pattern is considered a literal string and items
          returned if they contain the string.
        
        1) Simple pattern matching is similar as matching files in a shell and
        it is always case-sensitive. The special characters are presented below.
        
        '*'        - matches everything
        '?'        - matches any single character
        '[chars]'  - matches any character inside square brackets (e.g. '[abc]'
                     matches either 'a', 'b' or 'c')
        '[!chars]' - matches any character not inside square brackets
        
        Simple pattern matching is implemented using Python 'fnmatch' module's
        'fnmatchcase' method. For more information see its documentation at 
        http://docs.python.org/lib/module-fnmatch.html
          
        2) Regular expression check is done using Python 're' module which has 
        a pattern syntax derived from Perl and thus also very similar to the 
        one in Java. See following documents from more details about regexps
        in general and their Python implementation in particular.
        
        're' Module Documentation: http://docs.python.org/lib/module-re.html
        Regular Expression HOWTO: http://www.amk.ca/python/howto/regex/
        
        Note that if you want to use flags (e.g. re.IGNORECASE) you have to
        embed them into the pattern (e.g. '(?i)pattern'). Note also that 
        backslash is an escape character in Robot test data and possible
        backslaches in patterns must thus be escaped with another backslash
        (e.g. '\\\\d\\\\w+').
        """
        items = self._list_dir(path, pattern, pattern_type, absolute)
        for item in items:
            self._info(item)
        return items

    def list_files_in_directory(self, path, pattern=None, pattern_type='simple',
                          absolute=False):
        """A wrapper for 'List Directory' that returns only files."""
        files = self._list_files_in_dir(path, pattern, pattern_type, absolute)
        for f in files:
            self._info(f)
        return files
    
    def list_directories_in_directory(self, path, pattern=None, pattern_type='simple',
                         absolute=False):
        """A wrapper for 'List Directory' that returns only directories."""
        dirs = self._list_dirs_in_dir(path, pattern, pattern_type, absolute)
        for d in dirs: 
            self._info(d)
        return dirs

    def count_items_in_directory(self, path, pattern=None, pattern_type='simple'):
        """Returns the number of all items in the given directory.
        
        Arguments 'pattern' and 'pattern_type' have same semantics as in 'List
        Directory' keyword. Count is returned as an integer so it must be 
        checked e.g. with built-in keyword 'Should Be Equal As Integers'. 
        """
        items = self._list_dir(path, pattern, pattern_type)
        return len(items)
    
    def count_files_in_directory(self, path, pattern=None, pattern_type='simple'):
        """Returns the number of files in the given directory.
        
        Arguments 'pattern' and 'pattern_type' have same semantics as in 'List
        Directory' keyword. Count is returned as an integer so it must be 
        checked e.g. with built-in keyword 'Should Be Equal As Integers'. 
        """
        files = self._list_files_in_dir(path, pattern, pattern_type)
        return len(files)
    
    def count_directories_in_directory(self, path, pattern=None, pattern_type='simple'):
        """Returns the number of sub directories in the given directory.
        
        Arguments 'pattern' and 'pattern_type' have same semantics as in 'List
        Directory' keyword. Count is returned as an integer so it must be 
        checked e.g. with built-in keyword 'Should Be Equal As Integers'. 
        """
        dirs = self._list_dirs_in_dir(path, pattern, pattern_type)
        return len(dirs)

    def _list_dir(self, path, pattern=None, pattern_type='simple', 
                  absolute=False):
        if not os.path.isdir(path):
            raise DataError("Directory '%s' does not exist" % path)
        items = os.listdir(path)
        if pattern is None:
            pass
        elif utils.contains(pattern_type, 'simple'):
            items = [ i for i in items if fnmatch.fnmatchcase(i, pattern) ]
        elif utils.contains_any(pattern_type, ['regular expression','regexp']):
            grep = re.compile(pattern)
            items = [ i for i in items if grep.search(i) is not None ]
        else:
            items = [ i for i in items if i.count(pattern) > 0 ]
        items.sort()
        if utils.to_boolean(absolute, true_strs=['absolute'], default=False):
            path = utils.normpath(path)
            items = [ os.path.join(path,item) for item in items ]
        return items

    def _list_files_in_dir(self, path, pattern=None, pattern_type='simple',
                           absolute=False):
        return [ item for item in 
                 self._list_dir(path, pattern, pattern_type, absolute)
                 if os.path.isfile(os.path.join(path,item)) ]

    def _list_dirs_in_dir(self, path, pattern=None, pattern_type='simple',
                          absolute=False):
        return [ item for item in 
                 self._list_dir(path, pattern, pattern_type, absolute)
                 if os.path.isdir(os.path.join(path,item)) ]

    def touch(self, path):
        """Emulates Unix touch command.
        
        Creates file if it does not exist, otherwise changes its access and 
        modified times to current time.
        
        Fails if used with directories or parent directory of the given file 
        does not exist.
        """
        if os.path.isdir(path):
            raise DataError("Cannot touch '%s' because it is a directory" % path)
        if not os.path.exists(os.path.dirname(path)):
            raise DataError("Cannot touch '%s' because its parent directory "
                            "does not exist" % path)
        open(path, 'w').close()
        self._info("Touched file '%s'" % path)
            
    def _fail(self, error, default):
        if error is None:
            error = default
        raise AssertionError(error)

    def _info(self, msg):
        print "*INFO*", msg
        

class _Process:
    
    def __init__(self, command, input):
        stdin, self.stdout, self.stderr = os.popen3(command)
        if input != '':
            stdin.write(input)
        stdin.close()
        self.closed = False
        
    def read_stdout(self):
        out, err = self._read()
        if err != '':
            raise DataError('Stderr was not empty. Contents:\n%s' % err)
        return out
    
    def read_stderr(self):
        return self._read()[1]
    
    def read_stdout_and_stderr(self):
        return self._read()
        
    def _read(self):
        if self.closed:
            raise DataError('Cannot read from a closed process')
        err = self.stderr.read()
        out = self.stdout.read()
        self.close()
        return out, err
    
    def close(self):
        if not self.closed:
            self.stdout.close() 
            self.stderr.close()
            self.closed = True
