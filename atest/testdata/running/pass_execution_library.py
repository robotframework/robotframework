from robot.errors import ExecutionPassed
from robot.libraries.BuiltIn import BuiltIn

def keyword_from_library_throws_exception(msg):
    raise ExecutionPassed(msg)

def keyword_from_library_calls_builtin(msg):
    BuiltIn().pass_execution(msg, 'lol')
