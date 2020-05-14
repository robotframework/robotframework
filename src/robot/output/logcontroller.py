from robot.output.loggerhelper import AbstractLogger

def split_optional(s, delim):
    pos = s.find(delim)
    if pos > 0:
        return s[:pos], s[pos + 1:]
    else:
        return s, None


class LoggingState(object):
    def __init__(self, prev_state=None):
        if prev_state:
            self.remove_called = max(prev_state.remove_called - 1, 0)
        else:
            self.remove_called = 0
        self.log_here = self.remove_called == 0
        self.is_started = True

    def flatten(self, attribute):
        self.remove_called = int(attribute) if attribute else 0
        self.log_here = False

    def remove(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999
        self.log_here = False

    def reduce(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999


class LogController(AbstractLogger):
    def __init__(self, level='TRACE'):
        AbstractLogger.__init__(self, level)
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
        logging_state = LoggingState(self.current())
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

    def message(self, *args):
        return
