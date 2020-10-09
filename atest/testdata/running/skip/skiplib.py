from robot.errors import SkipExecution


class CustomSkipException(Exception):
    # TODO: make this work, add test
    ROBOT_SKIP_ON_FAILURE = True


def skip_with_message(msg):
    raise SkipExecution(msg)


def skip_with_custom_exception(self):
    raise CustomSkipException("Skipped with custom exception.")
