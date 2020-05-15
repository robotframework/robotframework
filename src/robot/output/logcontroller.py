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
        if prev_state:
            self.remove_called = max(prev_state.remove_called - 1, 0)
            self.message_is_logged = prev_state.message_is_logged
        else:
            self.remove_called = 0
            self.message_is_logged = IsLogged('TRACE')
        self.log_keyword_here = self.remove_called == 0
        self.keyword_is_started = True

    def flatten(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 0
        self.log_keyword_here = False

    def remove(self, attribute):
        if attribute:
            raise ValueError('Tag robot:Remove does not accept an attribute' + 
                             ' - all messaging is removed')
        self.remove_called = 999
        self.log_keyword_here = False
        self.message_is_logged = IsLogged('NONE')

    def reduce(self, attribute):
        self.remove_called = int(attribute) + 1 if attribute else 999

    actions = {
        'rf:flatten': flatten,
        'robot:flatten': flatten,
        'rf:remove': remove,
        'robot:remove': remove,
        'rf:reduce': reduce,
        'robot:reduce': reduce
    }

    def do_action(self, tag):
        tag, attribute = split_optional(tag, '-')
        try:
            action = self.actions[tag]
            action(self, attribute)
        except (ValueError, KeyError):
            return


class LogController(AbstractLogger):
    def __init__(self, level='TRACE'):
        AbstractLogger.__init__(self, level)
        self.start_test()

    def push(self, item):
        item.keyword_is_started = item.log_keyword_here or (
                                len(self.keyword_stack) < 2 and item.remove_called)
        self.keyword_stack.append(item)

    def current(self):
        return self.keyword_stack[-1]

    def start_test(self, test=None):
        state = LoggingState()
        state.message_is_logged = self._is_logged
        self.keyword_stack = list([state])

    def start_keyword(self, keyword):
        logging_state = LoggingState(self.current())
        for tag in keyword.tags:
            logging_state.do_action(tag)

        self.push(logging_state)
    
    def end_keyword(self, keyword):
        state = self.keyword_stack.pop()
        self._is_logged = self.current().message_is_logged

    def keyword_is_logged(self):
        return self.current().keyword_is_started

    def set_log_level(self, level):
        old = self.current().message_is_logged._str_level.upper()
        self.current().message_is_logged = IsLogged(level)
        return old

    def message_is_logged(self, level):
        return self.current().message_is_logged(level)

    def message(self, *args):
        return
