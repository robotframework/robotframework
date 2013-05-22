from robot.errors import PassExecution
from robot.libraries.BuiltIn import BuiltIn

def keyword_from_library_throws_exception(msg):
    raise PassExecution(msg)

def keyword_from_library_calls_builtin(msg):
    BuiltIn().pass_execution(msg, 'lol')
