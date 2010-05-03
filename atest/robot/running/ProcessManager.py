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
        args = args[0].split() + list(args[1:])
        self._process = subprocess.Popen(args, stderr=subprocess.PIPE, 
                                         stdout=subprocess.PIPE)
        self._stdout = ''
        self._stderr = ''

    def returncode(self):
        self._process.poll()
        return self._process.returncode

    def send_terminate(self, signal_name):
        if os.name != 'nt':
            signal_to_send = getattr(signal, signal_name)
            pid = self._process.pid
            os.kill(pid, signal_to_send)
        else:
            signal_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
            kernel32 = ctypes.windll.kernel32
            kernel32.GenerateConsoleCtrlEvent(0, 0)
            signal.signal(signal.SIGINT, signal_handler)

    def get_stdout(self):
        self._stdout += self._process.stdout.read()
        return self._stdout

    def get_stderr(self):
        self._stderr += self._process.stderr.read()
        return self._stderr

    def wait_until_finished(self):
        self._process.wait()

    def busy_sleep(self, seconds):
        max_time = time.time() + int(seconds)
        while time.time() < max_time:
            pass

    def get_jython_path(self):
        jython_home = os.getenv('JYTHON_HOME')
        if not jython_home:
            raise RuntimeError('This test requires JYTHON_HOME environment variable to be set.')
        return '%s -Dpython.home=%s -classpath %s org.python.util.jython' \
                % (self._get_java(), jython_home, self._get_classpath(jython_home))

    def _get_java(self):
        java_home = os.getenv('JAVA_HOME')
        if not java_home:
            return 'java'
        if java_home.startswith('"') and java_home.endswith('"'):
            java_home = java_home[1:-1]
        return os.path.join(java_home, 'bin', 'java')

    def _get_classpath(self, jython_home):
        jython_jar = os.path.join(jython_home, 'jython.jar')
        return jython_jar + os.pathsep + os.getenv('CLASSPATH','')

