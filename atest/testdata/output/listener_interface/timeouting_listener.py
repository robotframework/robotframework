from robot.errors import TimeoutExceeded


class timeouting_listener:
    ROBOT_LISTENER_API_VERSION = 2
    timeout = False

    def start_keyword(self, name, info):
        self.timeout = name == 'BuiltIn.Log'

    def end_keyword(self, name, info):
        self.timeout = False

    def log_message(self, message):
        if self.timeout:
            self.timeout = False
            raise TimeoutExceeded('Emulated timeout inside log_message')
