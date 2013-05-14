import re
from collections import namedtuple

from robot.utils import ET


MATCHER = re.compile(r'.*\((\w*) (.*) on (.*)\)')
Interpreter = namedtuple('Interpreter', ['interpreter', 'version', 'platform'])


def get_interpreter(output):
    tree = ET.parse(output)
    root = tree.getroot()
    return Interpreter(*MATCHER.match(root.attrib['generator']).groups())

def is_27(interpreter):
    return interpreter.version.startswith('2.7')

def is_25(interpreter):
    return interpreter.version.startswith('2.5')

def is_jython(interpreter):
    return interpreter.interpreter.lower() == 'jython'

def is_python(interpreter):
    return interpreter.interpreter.lower() == 'python'

