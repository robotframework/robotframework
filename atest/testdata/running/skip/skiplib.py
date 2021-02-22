from robot.api import SkipExecution


class CustomSkipException(Exception):
    ROBOT_SKIP_EXECUTION = True


def skip_with_message(msg):
    raise SkipExecution(msg)


def skip_with_custom_exception():
    raise CustomSkipException("Skipped with custom exception.")
