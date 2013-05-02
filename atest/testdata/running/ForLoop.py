
def raise_exit_for_loop():
    raise ExitForLoopException()

def raise_continue_for_loop():
    raise ContinueForLoopException()


class ExitForLoopException(Exception):
    ROBOT_EXIT_FOR_LOOP = 'yes please'


class ContinueForLoopException(Exception):
    ROBOT_CONTINUE_FOR_LOOP = 'yes please'
