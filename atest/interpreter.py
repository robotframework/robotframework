from os.path import abspath, dirname, exists, join
import os
import subprocess
import sys


PROJECT_ROOT = dirname(dirname(abspath(__file__)))
ROBOT_PATH = join(PROJECT_ROOT, 'src', 'robot')


def get_variables(path, name=None, version=None):
    return {'INTERPRETER': InterpreterFactory(path, name, version)}


def InterpreterFactory(path, name=None, version=None):
    if path.endswith('.jar'):
        return StandaloneInterpreter(path, name, version)
    return Interpreter(path, name, version)


class Interpreter(object):

    def __init__(self, path, name=None, version=None):
        self.path = path
        self.interpreter = self._get_interpreter(path)
        if not name:
            name, version = self._get_name_and_version()
        self.name = name
        self.version = version

    def _get_interpreter(self, path):
        return [path] if os.path.exists(path) else path.split()

    def _get_name_and_version(self):
        try:
            output = subprocess.check_output(self.interpreter + ['-V'],
                                             stderr=subprocess.STDOUT,
                                             encoding='UTF-8')
        except subprocess.CalledProcessError:
            raise ValueError('Invalid interpreter: %s' % self.path)
        name, version = output.split()[:2]
        name = name if 'PyPy' not in output else 'PyPy'
        version = '.'.join(version.split('.')[:2])
        return name, version

    @property
    def excludes(self):
        if self.is_jython:
            yield 'no-jython'
            yield 'require-lxml'
        else:
            yield 'require-jython'
        if self.is_ironpython:
            yield 'no-ipy'
            yield 'require-et13'
            yield 'require-lxml'
            yield 'require-docutils'  # https://github.com/IronLanguages/main/issues/1230
        else:
            yield 'require-ipy'
        for exclude in self._platform_excludes:
            yield exclude

    @property
    def _platform_excludes(self):
        if self.is_py3:
            yield 'no-py3'
        else:
            yield 'no-py2'
        if self.is_windows:
            yield 'no-windows'
            if self.is_jython:
                yield 'no-windows-jython'
        if not self.is_windows:
            yield 'require-windows'
        if self.is_osx:
            yield 'no-osx'
            if self.is_python:
                yield 'no-osx-python'

    @property
    def classpath(self):
        if not self.is_jython:
            return None
        classpath = os.environ.get('CLASSPATH')
        if classpath and 'tools.jar' in classpath:
            return classpath
        tools_jar = join(PROJECT_ROOT, 'ext-lib', 'tools.jar')
        if not exists(tools_jar):
            return classpath
        if classpath:
            return classpath + os.pathsep + tools_jar
        return tools_jar

    @property
    def is_python(self):
        return self.name == 'Python'

    @property
    def is_jython(self):
        return self.name == 'Jython'

    @property
    def is_ironpython(self):
        return self.name == 'IronPython'

    @property
    def is_pypy(self):
        return self.name == 'PyPy'

    @property
    def is_py2(self):
        return self.version[0] == '2'

    @property
    def is_py3(self):
        return self.version[0] == '3'

    @property
    def is_linux(self):
        return 'linux' in sys.platform

    @property
    def is_osx(self):
        return sys.platform == 'darwin'

    @property
    def is_windows(self):
        return os.name == 'nt'

    @property
    def os(self):
        for condition, name in [(self.is_linux, 'Linux'),
                                (self.is_osx, 'OS X'),
                                (self.is_windows, 'Windows')]:
            if condition:
                return name
        return sys.platform

    @property
    def runner(self):
        return self.interpreter + [join(ROBOT_PATH, 'run.py')]

    @property
    def rebot(self):
        return self.interpreter + [join(ROBOT_PATH, 'rebot.py')]

    @property
    def libdoc(self):
        return self.interpreter + [join(ROBOT_PATH, 'libdoc.py')]

    @property
    def testdoc(self):
        return self.interpreter + [join(ROBOT_PATH, 'testdoc.py')]

    @property
    def tidy(self):
        return self.interpreter + [join(ROBOT_PATH, 'tidy.py')]


class StandaloneInterpreter(Interpreter):

    def __init__(self, path, name=None, version=None):
        Interpreter.__init__(self, abspath(path), name or 'Standalone JAR',
                             version or '2.7')

    def _get_interpreter(self, path):
        interpreter = ['java', '-jar', path]
        classpath = self.classpath
        if classpath:
            interpreter.insert(1, '-Xbootclasspath/a:%s' % classpath)
        return interpreter

    @property
    def excludes(self):
        for exclude in ['no-standalone', 'no-jython', 'require-lxml',
                        'require-docutils', 'require-ipy']:
            yield exclude
        for exclude in self._platform_excludes:
            yield exclude

    @property
    def is_python(self):
        return False

    @property
    def is_jython(self):
        return True

    @property
    def is_ironpython(self):
        return False

    @property
    def runner(self):
        return self.interpreter + ['run']

    @property
    def rebot(self):
        return self.interpreter + ['rebot']

    @property
    def libdoc(self):
        return self.interpreter + ['libdoc']

    @property
    def testdoc(self):
        return self.interpreter + ['testdoc']

    @property
    def tidy(self):
        return self.interpreter + ['tidy']
