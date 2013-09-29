import re
try:
    from collections import namedtuple
except ImportError:
    pass

from robot.utils import ET


MATCHER = re.compile(r'.*\((\w*) (.*) on (.*)\)')
try:
    Interpreter = namedtuple('Interpreter', ['interpreter', 'version', 'platform'])
except NameError:
    class Interpreter(tuple):
        def __new__(cls, *values):
            return tuple.__new__(cls, values)

        def __init__(self, interpreter, version, platform):
            self.interpreter = interpreter
            self.version = version
            self.platform = platform

def get_interpreter(output):
    tree = ET.parse(output)
    root = tree.getroot()
    return Interpreter(*MATCHER.match(root.attrib['generator']).groups())

def is_3x(interpreter):
    return interpreter.version.startswith('3')

def is_2x(interpreter):
    return interpreter.version.startswith('2')

def is_27(interpreter):
    return interpreter.version.startswith('2.7')

def is_25(interpreter):
    return interpreter.version.startswith('2.5')

def is_jython(interpreter):
    return interpreter.interpreter.lower() == 'jython'

def is_python(interpreter):
    return interpreter.interpreter.lower() == 'python'

