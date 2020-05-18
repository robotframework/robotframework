from robot.output.loggerhelper import AbstractLogger, IsLogged
from copy import copy

def split_optional(s, delim):
    pos = s.find(delim)
    if pos > 0:
        return s[:pos], s[pos + 1:]
    else:
        return s, None


class LoggingState(object):
    def __init__(self, prev_state=None):
        self.message_is_logged = None
        if prev_state:
            self.remove_called = max(prev_state.remove_called - 1, 0)
            if self.remove_called:
                self.message_is_logged = prev_state.message_is_logged
        else:
            self.remove_called = 0
        self.log_keyword_here = self.remove_called == 0
        self.keyword_is_started = True

    def flatten(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 0
        self.log_keyword_here = False

    def remove(self, attribute):
        self.remove_called = 999
        self.log_keyword_here = False
        self.message_is_logged = IsLogged('NONE')

    def reduce(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999

    def restore(self, attribute):
        self.remove_called = 0
        self.log_keyword_here = True

    actions = {
        'robot:flatten': flatten,
        'robot:remove': remove,
        'robot:reduce': reduce,
        'robot:restore': restore
    }

    def do_action(self, tag):
        tag, attribute = split_optional(tag, '-')
        try:
            action = self.actions[tag.lower()]
            action(self, attribute)
        except (ValueError, KeyError):
            return
        return True


class LogController(AbstractLogger):
    def __init__(self, level='TRACE'):
        AbstractLogger.__init__(self, level)
        self.start_test()

    def push(self, item):
        item.keyword_is_started = item.log_keyword_here or (
                                len(self.keyword_stack) < 2 and item.remove_called)
        if item.message_is_logged:
            self.current().message_is_logged = self._is_logged
            self._is_logged = item.message_is_logged
        self.keyword_stack.append(item)

    def current(self):
        return self.keyword_stack[-1]

    def keyword_logging(self, level):
        if len(self.keyword_stack) < 2:
            return
        return self.keyword_stack[-2].do_action(level)

    def start_test(self, test=None):
        state = LoggingState()
        self.keyword_stack = list([state])

    def start_keyword(self, keyword):
        previous_state = self.current()
        logging_state = LoggingState(previous_state)
        for tag in keyword.tags:
            logging_state.do_action(tag)

        if previous_state.message_is_logged and not logging_state.message_is_logged:
            # Restore message logging to what it was before tags got involved
            for i in range(len(self.keyword_stack) - 1, -1, -1):
                earlier_logged = self.keyword_stack[i].message_is_logged
                if not earlier_logged:
                    break
                self._is_logged = self.keyword_stack[i].message_is_logged

        self.push(logging_state)
    
    def end_keyword(self, keyword):
        state = self.keyword_stack.pop()
        if self.current().message_is_logged:
            self._is_logged = self.current().message_is_logged

    def keyword_is_logged(self):
        return self.current().keyword_is_started

    def message_is_logged(self, level):
        current = self.current().message_is_logged
        if not current:
            current = self._is_logged
        return current(level)

    def message(self, *args):
        return
