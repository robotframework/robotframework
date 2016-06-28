from robot.errors import PassExecution
from robot.libraries.BuiltIn import BuiltIn


def raise_pass_execution_exception(msg):
    raise PassExecution(msg)


def call_pass_execution_method(msg):
    BuiltIn().pass_execution(msg, 'lol')
