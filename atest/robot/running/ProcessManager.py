import subprocess
import os
import signal
import ctypes
import time


class ProcessManager(object):

    def __init__(self):
        self._process = None
        self._stdout = ''
        self._stderr = ''

    def start_process(self, *args):
        self._process = subprocess.Popen(args, stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE)
        self._stdout = ''
        self._stderr = ''

    def send_terminate(self, signal_name):
        if os.name != 'nt':
            os.kill(self._process.pid, getattr(signal, signal_name))
        else:
            self._set_handler_to_ignore_one_sigint()
            ctypes.windll.kernel32.GenerateConsoleCtrlEvent(0, 0)

    def _set_handler_to_ignore_one_sigint(self):
        orig_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda signum, frame:
                      signal.signal(signal.SIGINT, orig_handler))

    def get_stdout(self):
        self.wait_until_finished()
        return self._stdout

    def get_stderr(self):
        self.wait_until_finished()
        return self._stderr

    def log_stdout_and_stderr(self):
        print "stdout: ", self._process.stdout.read()
        print "stderr: ", self._process.stderr.read()

    def wait_until_finished(self):
        if self._process.returncode is None:
            self._stdout, self._stderr = self._process.communicate()

    def busy_sleep(self, seconds):
        max_time = time.time() + int(seconds)
        while time.time() < max_time:
            pass

    def get_jython_path(self):
        jython_home = os.getenv('JYTHON_HOME')
        if not jython_home:
            raise RuntimeError('This test requires JYTHON_HOME environment variable to be set.')
        return [self._get_java(), '-Dpython.home=%s' % jython_home,
                '-classpath',  self._get_classpath(jython_home),
                'org.python.util.jython']

    def _get_java(self):
        java_home = os.getenv('JAVA_HOME')
        if not java_home:
            return 'java'
        if java_home.startswith('"') and java_home.endswith('"'):
            java_home = java_home[1:-1]
        return os.path.join(java_home, 'bin', 'java')

    def _get_classpath(self, jython_home):
        jython_jar = os.path.join(jython_home, 'jython.jar')
        cp = jython_jar + os.pathsep + os.getenv('CLASSPATH', '')
        return cp.strip(':;')

