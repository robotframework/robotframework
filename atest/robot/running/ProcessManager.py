import subprocess
import os
import signal
import ctypes


class ProcessManager(object):

    def __init__(self):
        self._process = None
        self._stdout = None
        self._stderr = None

    def start_process(self, *args):
        self._process = subprocess.Popen(args, stderr=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         universal_newlines=True)
        self._stdout = None
        self._stderr = None

    def send_terminate(self, signal_name):
        if os.name != 'nt':
            os.kill(self._process.pid, getattr(signal, signal_name))
        else:
            # TODO: This approach does not work in CI and/or current
            # windows environments as it tries to kill the parent process
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
        self.wait_until_finished()
        print('STDOUT:')
        print(self._stdout)
        print('STDERR:')
        print(self._stderr)

    def wait_until_finished(self):
        if self._stdout is None:
            self._stdout, self._stderr = self._process.communicate()

    def get_runner(self, interpreter, robot_path):
        run = os.path.join(robot_path, 'run.py')
        if 'jython' not in interpreter:
            return [interpreter, run]
        jython_home = os.getenv('JYTHON_HOME')
        if not jython_home:
            raise RuntimeError('This test requires JYTHON_HOME environment variable to be set.')
        return [self._get_java(), '-Dpython.home=%s' % jython_home,
                '-classpath',  self._get_classpath(jython_home),
                'org.python.util.jython', run]

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
