import time

from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

MSG = "A rather long message that is slow to write on the disk. " * 10000


def log_messages_and_set_log_level():
    b = BuiltIn()
    b.log("Should not be logged because current level is INFO.", "DEBUG")
    b.set_log_level("NONE")
    b.log("Not logged!", "WARN")
    b.set_log_level("DEBUG")
    b.log("Hello, debug world!", "DEBUG")


def get_test_name():
    return BuiltIn().get_variables()["${TEST NAME}"]


def set_secret_variable():
    BuiltIn().set_test_variable("${SECRET}", "*****")


def named_argument_syntax():
    b = BuiltIn()
    b.should_be_equal(b.get_variable_value("${existing}", default=123), 42)
    b.should_be_equal(b.get_variable_value("${nonexisting}", default=123), 123)
    b.variable_should_exist("${existing}", message="This succeeds!")
    b.variable_should_not_exist("${nonexisting}", message="This succeeds!")
    b.pass_execution_if(True, message="The end!")


def use_run_keyword_with_non_string_values():
    BuiltIn().run_keyword("Log", 42)
    BuiltIn().run_keyword("Log", b"\xff")


def user_keyword_via_run_keyword():
    logger.info("Before")
    BuiltIn().run_keyword("UseBuiltInResource.Keyword", "This is x", 911)
    logger.info("After")


def recursive_run_keyword(limit: int, round: int = 1):
    if round <= limit:
        BuiltIn().run_keyword("Log", round)
        BuiltIn().run_keyword("Recursive Run Keyword", limit, round + 1)


def run_keyword_that_logs_huge_message_until_timeout():
    while True:
        BuiltIn().run_keyword("Log Huge Message")


def log_huge_message():
    logger.info(MSG)


def timeout_in_parent_keyword_after_running_keyword():
    BuiltIn().run_keyword("Log", "Hello!")
    while True:
        time.sleep(0)
