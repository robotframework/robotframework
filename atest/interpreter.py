from os.path import abspath, dirname, exists, join
import os
import re
import subprocess
import sys


PROJECT_ROOT = dirname(dirname(abspath(__file__)))
ROBOT_PATH = join(PROJECT_ROOT, 'src', 'robot')


def get_variables(path, name=None, version=None):
    interpreter = InterpreterFactory(path, name, version)
    u = '' if interpreter.is_py3 or interpreter.is_ironpython else 'u'
    return {'INTERPRETER': interpreter, 'UNICODE PREFIX': u}


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
        self.version_info = tuple(int(item) for item in version.split('.'))
        self.java_version_info = self._get_java_version_info()

    def _get_interpreter(self, path):
        path = path.replace('/', os.sep)
        return [path] if os.path.exists(path) else path.split()

    def _get_name_and_version(self):
        try:
            output = subprocess.check_output(self.interpreter + ['-V'],
                                             stderr=subprocess.STDOUT,
                                             encoding='UTF-8')
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            raise ValueError('Failed to get interpreter version: %s' % err)
        name, version = output.split()[:2]
        name = name if 'PyPy' not in output else 'PyPy'
        version = re.match(r'\d+\.\d+\.\d+', version).group()
        return name, version

    def _get_java_version_info(self):
        if not self.is_jython:
            return -1, -1
        try:
            # platform.java_ver() returns Java version in a format:
            # ('9.0.7.1', ...) or ('11.0.6', ...) or ('1.8.0_121', ...)
            script = 'import platform; print(platform.java_ver()[0])'
            output = subprocess.check_output(self.interpreter + ['-c', script],
                                             stderr=subprocess.STDOUT,
                                             encoding='UTF-8')
        except (subprocess.CalledProcessError, FileNotFoundError) as err:
            raise ValueError('Failed to get Java version: %s' % err)
        version = [int(re.match(r'\d*', v).group() or 0) for v in output.split('.')]
        missing = [0] * (2 - len(version))
        return tuple(version + missing)[:2]

    @property
    def os(self):
        for condition, name in [(self.is_linux, 'Linux'),
                                (self.is_osx, 'OS X'),
                                (self.is_windows, 'Windows')]:
            if condition:
                return name
        return sys.platform

    @property
    def output_name(self):
        return '{i.name}-{i.version}-{i.os}'.format(i=self).replace(' ', '')

    @property
    def excludes(self):
        if not self.is_python:
            yield 'require-lxml'
        if self.is_jython:
            yield 'no-jython'
            if self.version_info[:3] == (2, 7, 0):
                yield 'no-jython-2.7.0'
            if self.version_info[:3] == (2, 7, 1):
                yield 'no-jython-2.7.1'
        else:
            yield 'require-jython'
        if self.is_ironpython:
            yield 'no-ipy'
            yield 'require-docutils'  # https://github.com/IronLanguages/main/issues/1230
        else:
            yield 'require-ipy'
        for exclude in self._platform_excludes:
            yield exclude

    @property
    def _platform_excludes(self):
        if self.is_py3:
            yield 'require-py2'
        else:
            yield 'require-py3'
        if self.version_info[:2] == (3, 5):
            yield 'no-py-3.5'
        for require in [(3, 5), (3, 6), (3, 7), (3, 8), (3, 9), (3, 10)]:
            if self.version_info < require:
                yield 'require-py%d.%d' % require
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
        if self.java_version_info[0] >= 9 or classpath and 'tools.jar' in classpath:
            return classpath
        tools_jar = join(PROJECT_ROOT, 'ext-lib', 'tools.jar')
        if not exists(tools_jar):
            return classpath
        if classpath:
            return classpath + os.pathsep + tools_jar
        return tools_jar

    @property
    def java_opts(self):
        if not self.is_jython:
            return None
        java_opts = os.environ.get('JAVA_OPTS', '')
        if self.version_info[:3] >= (2, 7, 2) and self.java_version_info[0] >= 9:
            # https://github.com/jythontools/jython/issues/171
            if '--add-opens' not in java_opts:
                java_opts += ' --add-opens java.base/java.io=ALL-UNNAMED --add-opens java.base/sun.nio.ch=ALL-UNNAMED'
        return java_opts

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
    def is_standalone(self):
        return False

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

    def __str__(self):
        java = ''
        if self.is_jython:
            java = '(Java %s) ' % '.'.join(str(ver_part) for ver_part in self.java_version_info)
        return '%s %s %son %s' % (self.name, self.version, java, self.os)


class StandaloneInterpreter(Interpreter):

    def __init__(self, path, name=None, version=None):
        Interpreter.__init__(self, abspath(path), name or 'Standalone JAR',
                             version or '2.7.2')
        if self.classpath:
            self.interpreter.insert(1, '-Xbootclasspath/a:%s' % self.classpath)

    def _get_interpreter(self, path):
        java_home = os.environ.get('JAVA_HOME')
        java = join(java_home, 'bin', 'java') if java_home else 'java'
        return [java, '-jar', path]

    def _get_java_version_info(self):
        result = subprocess.run(self.interpreter + ['--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                encoding='UTF-8')
        if result.returncode != 251:
            raise ValueError('Failed to get Robot Framework version:\n%s'
                             % result.stdout)
        match = re.search(r'Jython .* on java(\d+)(\.(\d+))?', result.stdout)
        if not match:
            raise ValueError("Failed to find Java version from '%s'."
                             % result.stdout)
        return int(match.group(1)), int(match.group(3) or 0)

    @property
    def excludes(self):
        for exclude in ['no-standalone', 'no-jython', 'require-lxml',
                        'require-docutils', 'require-enum', 'require-ipy']:
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
    def is_pypy(self):
        return False

    @property
    def is_standalone(self):
        return True

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
