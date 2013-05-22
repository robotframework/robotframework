def raise_exit_for_loop():
    raise ExitForLoopException()

class ExitForLoopException(Exception):
    ROBOT_EXIT_FOR_LOOP = 'yes please'
