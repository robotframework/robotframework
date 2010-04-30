class FatalCatastrophyException(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True

class ContinuableApocalypseException(RuntimeError):
    ROBOT_CONTINUE_ON_FAILURE = True

def exit_on_failure():
    raise FatalCatastrophyException()

def raise_continuable_failure(msg='Can be continued'):
    raise ContinuableApocalypseException(msg)
