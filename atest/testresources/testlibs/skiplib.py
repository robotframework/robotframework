from robot.errors import SkipExecution

class skiplib:

    def skip_with_message(self, msg):
        raise SkipExecution(msg)
