from robot.output.loggerhelper import AbstractLogger

def split_optional(s, delim):
    pos = s.find(delim)
    if pos > 0:
        return s[:pos], s[pos + 1:]
    else:
        return s, None


class LoggingState(object):
    def __init__(self):
        self.log_here = True
        self.remove_called = 0
        self.is_started = True

    def next_level(self):
        next_state = LoggingState()
        remove_remaining = max(self.remove_called - 1, 0)
        next_state.log_here = remove_remaining == 0
        next_state.remove_called = remove_remaining
        return next_state

    def flatten(self, attribute):
        self.remove_called = int(attribute) if attribute else 0
        self.log_here = False

    def remove(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999
        self.log_here = False

    def reduce(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999

    def __str__(self):
        return f'{self.log_here}-{self.remove_called}-{self.is_started}'


class LogController(AbstractLogger):
    def __init__(self):
        self.start_test()

    def push(self, item):
        item.is_started = item.log_here or (
                                len(self.keyword_stack) < 2 and item.remove_called)
        self.keyword_stack.append(item)

    def current(self):
        return self.keyword_stack[-1]

    def start_test(self, test=None):
        self.keyword_stack = list([LoggingState()])

    def start_keyword(self, keyword):
        logging_state = self.current().next_level()
        for tag in keyword.tags:
            sentenal, tag = split_optional(tag, ':')
            if not sentenal in ['rf', 'robot']:
                continue
            tag, attribute = split_optional(tag, '-')
            try:
                getattr(logging_state, tag)(attribute)
            except (ValueError, AttributeError):
                continue

        self.push(logging_state)
    
    def end_keyword(self, keyword):
        self.keyword_stack.pop()

    def should_log(self):
        return self.current().is_started

    def _do_nothing(self, *args):
        return

    message = log_message = output_file = _imported = close = _do_nothing
    start_suite = end_suite = end_test = _do_nothing
