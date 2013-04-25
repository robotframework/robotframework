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
import sys
import tempfile

from robot.utils import ConnectionCache
from robot.version import get_version


class Process(object):
    """Robot Framework test library for running processes.
    """

    ROBOT_LIBRARY_SCOPE='GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def __init__(self):
        self._started_processes = ConnectionCache()
        self._logs = dict()
        self._tempdir = tempfile.mkdtemp(suffix="processlib")

    def run_process(self, command, *args, **conf):
        active_process_index = self._started_processes.current_index
        try:
            p = self.start_new_process(command, *args, **conf)
            return self.wait_for_process(p)
        finally:
            self._started_processes.switch(active_process_index)

    def start_new_process(self, command, *args, **conf):
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
        return self._process(handle).poll() is None

    def process_should_be_alive(self, handle=None):
        if not self.process_is_alive(handle):
            raise AssertionError('Process is not alive')

    def process_should_be_dead(self, handle=None):
        if self.process_is_alive(handle):
            raise AssertionError('Process is alive')

    def wait_for_process(self, handle=None):
        process = self._process(handle)
        result = self._logs[process]
        result.exit_code = process.wait()
        return result

    def terminate_process(self, handle=None, kill=False):
        process = self._process(handle)
        if kill:
            process.kill()
        else:
            process.terminate()

    def kill_all_processes(self):
        for handle in range(len(self._started_processes._connections)):
            if self.process_is_alive(handle):
                self.terminate_process(handle, kill=True)

    def get_process_id(self, handle=None):
        return self._process(handle).pid

    def input_to_process(self, msg, handle=None):
        self._process(handle).communicate(msg+'\n')

    def switch_active_process(self, handle):
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
