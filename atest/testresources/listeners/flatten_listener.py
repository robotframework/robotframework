class Listener:
    ROBOT_LISTENER_API_VERSION = '2'

    def __init__(self):
        self.start_kw_count = 0
        self.end_kw_count = 0

    def start_keyword(self, kw, attrs):
        self.start_kw_count += 1

    def end_keyword(self, kw, attrs):
        self.end_kw_count += 1

    def end_suite(self, *args):
        if not self.start_kw_count:
            raise AssertionError("No keywords started")
        if not self.end_kw_count:
            raise AssertionError("No keywords ended")
