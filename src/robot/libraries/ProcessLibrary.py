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
from __future__ import unicode_literals
import subprocess
import tempfile
from robot.utils import ConnectionCache

class ProcessData(object):

    def __init__(self, stdout, stderr):
        self.stdout = stdout
        self.stderr = stderr

class ProcessLibrary(object):

    def __init__(self):
        self._started_processes = ConnectionCache()
        self._logs = dict()
        self._tempdir = tempfile.mkdtemp(suffix="processlib")

    def run_process(self, command, *args, **conf):
        p = self.start_new_process(command, *args, **conf)
        return self.wait_for_process(p)

    def start_new_process(self, command, *args, **conf):
        cmd = [command]+[str(i) for i in args]
        config = _NewProcessConfig(conf, self._tempdir)
        stdout_stream = config.stdout_stream
        stderr_stream = config.stderr_stream
        pd = ProcessData(stdout_stream.name, stderr_stream.name)
        use_shell = config.use_shell
        if use_shell and args:
            cmd = subprocess.list2cmdline(cmd)
            print cmd
        p = subprocess.Popen(cmd, stdout=stdout_stream, stderr=stderr_stream,
                             shell=use_shell, cwd=config.cwd)
        index = self._started_processes.register(p, alias=config.alias)
        self._logs[index] = pd
        return index

    def process_is_alive(self, handle=None):
        if handle:
            self._started_processes.switch(handle)
        return self._started_processes.current.poll() is None

    def process_should_be_alive(self, handle):
        if not self.process_is_alive(handle):
            raise AssertionError('Process is not alive')

    def process_should_be_dead(self, handle):
        if self.process_is_alive(handle):
            raise AssertionError('Process is alive')

    def wait_for_process(self, handle=None):
        if handle:
            self._started_processes.switch(handle)
        exit_code = self._started_processes.current.wait()
        logs = self._logs[handle]
        with open(logs.stdout,'r') as f:
            stdout = f.read()
        with open(logs.stderr,'r') as f:
            stderr = f.read()
        return ExecutionResult(stdout, stderr, exit_code)

    def kill_process(self, handle=None):
        if handle:
            self._started_processes.switch(handle)
        self._started_processes.current.kill()

    def terminate_process(self, handle=None):
        if handle:
            self._started_processes.switch(handle)
        self._started_processes.current.terminate()

    def kill_all_processes(self):
        for handle in range(len(self._started_processes._connections)):
            self.kill_process(handle)

    def get_process_id(self, handle):
        self._started_processes.switch(handle)
        return self._started_processes.current.pid

    def input_to_process(self, handle, msg):
        if not msg:
            return
        alog = self._logs[handle]
        self._started_processes.switch(handle)
        self._started_processes.current.wait()
        with open(alog.stdout,'a') as f:
            f.write(msg.encode('UTF-8'))


class ExecutionResult(object):

    def __init__(self, stdout=None, stderr=None, exit_code=None):
        self.stdout = stdout or ''
        self.stderr = stderr or ''
        self.exit_code = exit_code


if __name__ == '__main__':
    r = ProcessLibrary().run_process('python', '-c', "print \'hello\'")
    print repr(r.stdout)

class _NewProcessConfig(object):

    def __init__(self, conf, tempdir):
        self._tempdir = tempdir
        self._conf = conf
        self.stdout_stream = open(conf['stdout'], 'w') if 'stdout' in conf else self._get_temp_file("stdout")
        self.stderr_stream = open(conf['stderr'], 'w') if 'stderr' in conf else self._get_temp_file("stderr")
        self.use_shell = (conf.get('shell', 'False') != 'False')
        self.cwd = conf.get('cwd', None)
        self.alias = conf.get('alias', None)


    def _get_temp_file(self, suffix):
        return tempfile.NamedTemporaryFile(delete=False,
                                           prefix='tmp_logfile_',
                                           suffix="_%s" % suffix,
                                           dir=self._tempdir)
