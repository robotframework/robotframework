from robot.api import ContinuableFailure, FatalError


class FatalCatastrophyException(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class ContinuableApocalypseException(RuntimeError):
    ROBOT_CONTINUE_ON_FAILURE = True


def exit_on_failure(msg='BANG!', standard=False):
    exception = FatalError if standard else FatalCatastrophyException
    raise exception(msg)


def raise_continuable_failure(msg='Can be continued', standard=False):
    exception = ContinuableFailure if standard else ContinuableApocalypseException
    raise exception(msg)
