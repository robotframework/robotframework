import subprocess
import os
import signal

class ProcessManager(object):

    def __init__(self):
        self._current_running_process = None

    def start_process(self, *args):
        if ' ' in args[0]:
            args = args[0].split() + list(args[1:])
        print args
        print ' '.join(args)
        self._current_running_process = subprocess.Popen(args, shell=False, stderr=subprocess.PIPE, 
                                                         stdout=subprocess.PIPE)
        self._output = ''
        self._err = ''

    def returncode(self):
        self._current_running_process.poll()
        return self._current_running_process.returncode

    def send_terminate(self, signal_name):
        signal_to_send = getattr(signal, signal_name)
        pid = self._current_running_process.pid
        if not os.name == 'nt':
            os.kill(pid, signal_to_send)
        else:
            print "Process pid is:", pid
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.GenerateConsoleCtrlEvent(0, 0)

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