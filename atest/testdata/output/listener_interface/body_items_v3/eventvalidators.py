class EventValidator:

    def __init__(self):
        self.events = iter([
            'KEYWORD',
            'KEYWORD', 'KEYWORD', 'RETURN',
            'IF/ELSE ROOT',
                'IF', 'KEYWORD',
                'ELSE IF', 'KEYWORD', 'KEYWORD', 'RETURN',
                'ELSE', 'KEYWORD',
            'TRY/EXCEPT ROOT',
                'TRY', 'KEYWORD',
                'EXCEPT', 'KEYWORD',
                'ELSE', 'KEYWORD',
                'FINALLY', 'KEYWORD', 'KEYWORD', 'RETURN',
            'FOR',
                'ITERATION', 'CONTINUE',
                'ITERATION', 'CONTINUE',
                'ITERATION', 'CONTINUE',
            'WHILE',
                'ITERATION', 'BREAK',
            'VAR', 'VAR', 'KEYWORD',
            'KEYWORD',
            'KEYWORD',
            'KEYWORD',
            'KEYWORD',
            'ERROR',
            'TEARDOWN'
        ])
        self.started = []
        self.errors = []

    def error(self, message):
        self.error(message)

    def validate(self):
        if self.errors:
            raise AssertionError(f'{len(self.errors)} errors in {type(self).__name__} '
                                 f'listener:\n' + '\n'.join(self.errors))
        if len(self.started) == 1:
            data, result = self.started[0]
            if data.type == result.type == 'TEARDOWN':
                return
        raise AssertionError('Mismatching start/end events.')

    def validate_start(self, data, result):
        event = next(self.events, None)
        if data.type != result.type:
            self.error('Mismatching data and result types.')
        if data.type != event:
            self.error(f'Expected event {event}, got {data.type}.')
        self.started.append((data, result))

    def validate_end(self, data, result):
        start_data, start_result = self.started.pop()
        if data is not start_data or result is not start_result:
            self.error('Mismatching start/end arguments.')


class StartEndBobyItemOnly(EventValidator):

    def start_body_item(self, data, result):
        self.validate_start(data, result)

    def endBodyItem(self, data, result):
        self.validate_end(data, result)


class SeparateMethods(EventValidator):

    def startKeyword(self, data, result):
        self.validate_start(data, result)

    def end_keyword(self, data, result):
        self.validate_end(data, result)

    def start_if(self, data, result):
        self.validate_start(data, result)

    def end_if(self, data, result):
        self.validate_end(data, result)

    def start_if_branch(self, data, result):
        self.validate_start(data, result)

    def endIfBranch(self, data, result):
        self.validate_end(data, result)

    def start_try(self, data, result):
        self.validate_start(data, result)

    def end_try(self, data, result):
        self.validate_end(data, result)

    def start_try_branch(self, data, result):
        self.validate_start(data, result)

    def end_try_branch(self, data, result):
        self.validate_end(data, result)

    def start_for(self, data, result):
        self.validate_start(data, result)

    def end_for(self, data, result):
        self.validate_end(data, result)

    def startForIteration(self, data, result):
        self.validate_start(data, result)

    def end_for_iteration(self, data, result):
        self.validate_end(data, result)

    def start_while(self, data, result):
        self.validate_start(data, result)

    def end_while(self, data, result):
        self.validate_end(data, result)

    def start_while_iteration(self, data, result):
        self.validate_start(data, result)

    def end_while_iteration(self, data, result):
        self.validate_end(data, result)

    def start_var(self, data, result):
        self.validate_start(data, result)

    def end_var(self, data, result):
        self.validate_end(data, result)

    def start_continue(self, data, result):
        self.validate_start(data, result)

    def end_continue(self, data, result):
        self.validate_end(data, result)

    def start_break(self, data, result):
        self.validate_start(data, result)

    def endBreak(self, data, result):
        self.validate_end(data, result)

    def start_return(self, data, result):
        self.validate_start(data, result)

    def end_return(self, data, result):
        self.validate_end(data, result)

    def start_error(self, data, result):
        self.validate_start(data, result)

    def end_error(self, data, result):
        self.validate_end(data, result)

    def start_body_item(self, data, result):
        self.error('Should not be called.')

    def end_body_item(self, data, result):
        self.error('Should not be called.')


class SeparateMethodsAlsoForKeywords(SeparateMethods):

    def start_user_keyword(self, data, implementation, result):
        if implementation.type != implementation.USER_KEYWORD:
            self.error('Invalid implementation type.')
        self.validate_start(data, result)

    def endUserKeyword(self, data, implementation, result):
        if implementation.type != implementation.USER_KEYWORD:
            self.error('Invalid implementation type.')
        self.validate_end(data, result)

    def start_library_keyword(self, data, implementation, result):
        if implementation.type != implementation.LIBRARY_KEYWORD:
            self.error('Invalid implementation type.')
        self.validate_start(data, result)

    def end_library_keyword(self, data, implementation, result):
        if implementation.type != implementation.LIBRARY_KEYWORD:
            self.error('Invalid implementation type.')
        self.validate_end(data, result)

    def startInvalidKeyword(self, data, implementation, result):
        if not implementation.error:
            self.error('Invalid implementation type.')
        self.validate_start(data, result)

    def end_invalid_keyword(self, data, implementation, result):
        if not implementation.error:
            self.error('Invalid implementation type.')
        self.validate_end(data, result)

    def start_keyword(self, data, result):
        self.error('Should not be called.')

    def end_keyword(self, data, result):
        self.error('Should not be called.')
