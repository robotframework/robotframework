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
import subprocess
import tempfile
import os
from robot.utils import ConnectionCache

class ProcessData(object):

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

class ProcessLibrary(object):
    ROBOT_LIBRARY_SCOPE='GLOBAL'

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
        cmd = [command]+[str(i) for i in args]
        config = _NewProcessConfig(conf, self._tempdir)
        stdout_stream = config.stdout_stream
        stderr_stream = config.stderr_stream
        pd = ProcessData(stdout_stream.name, stderr_stream.name)
        use_shell = config.use_shell
        if use_shell and args:
            cmd = subprocess.list2cmdline(cmd)
        elif use_shell:
            cmd = command
        p = subprocess.Popen(cmd, stdout=stdout_stream, stderr=stderr_stream,
                             shell=use_shell, cwd=config.cwd)
        index = self._started_processes.register(p, alias=config.alias)
        self._logs[index] = pd
        return index

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
        exit_code = process.wait()
        logs = self._logs[handle]
        return ExecutionResult(logs.stdout, logs.stderr, exit_code)

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

    def input_to_process(self, handle, msg):
        if not msg:
            return
        alog = self._logs[handle]
        self._started_processes.switch(handle)
        self._started_processes.current.wait()
        with open(alog.stdout,'a') as f:
            f.write(msg.encode('UTF-8'))

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


class _NewProcessConfig(object):

    def __init__(self, conf, tempdir):
        self._tempdir = tempdir
        self._conf = conf
        self.cwd = conf.get('cwd', os.path.abspath(os.curdir))
        self.stdout_stream = open(os.path.join(self.cwd,conf['stdout']), 'w') if 'stdout' in conf else self._get_temp_file("stdout")
        self.stderr_stream = self._get_stderr(conf)
        self.use_shell = (conf.get('shell', 'False') != 'False')
        self.alias = conf.get('alias', None)


    def _get_stderr(self, conf):
        if 'stderr' in conf:
            if conf['stderr'] == 'STDOUT' or conf['stderr'] == conf.get('stdout', None):
               return self.stdout_stream
        return open(os.path.join(self.cwd,conf['stderr']), 'w') if 'stderr' in conf else self._get_temp_file("stderr")

    def _get_temp_file(self, suffix):
        return tempfile.NamedTemporaryFile(delete=False,
                                           prefix='tmp_logfile_',
                                           suffix="_%s" % suffix,
                                           dir=self._tempdir)
