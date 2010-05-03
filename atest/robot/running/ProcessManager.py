import subprocess
import os
import signal

class ProcessManager(object):

    def __init__(self):
        self._current_running_process = None

    def start_process(self,*args):
        self._current_running_process = subprocess.Popen(args, shell=True, stderr=subprocess.PIPE, 
                                                         stdout=subprocess.PIPE)
        self._output = ''
        self._err = ''

    def returncode(self):
        self._current_running_process.poll()
        return self._current_running_process.returncode

    def send_terminate(self, signal_):
        pid = self._current_running_process.pid
        os.kill(pid, getattr(signal, signal_))

    def get_stdout(self):
        self._output += self._current_running_process.stdout.read()
        return self._output

    def get_stderr(self):
        self._err += self._current_running_process.stderr.read()
        return self._err

    def wait_until_finished(self):
        self._current_running_process.wait()

    def wait_until_err_contains(self, search):
        while not search in self.get_stderr():
            pass