from robot.running import (InvalidKeyword,
                           Keyword as KeywordData,
                           KeywordImplementation,
                           LibraryKeyword,
                           TestCase,
                           UserKeyword)
from robot.result import Keyword as KeywordResult


class DataModifier:
    modify_once = 'User keyword'

    def start_library_keyword(self, data: KeywordData,
                              implementation: LibraryKeyword,
                              result: KeywordResult):
        if isinstance(data.parent, TestCase) and data.parent.name == 'Library keyword':
            implementation.owner.instance.state = 'set by listener'

    def start_user_keyword(self, data: KeywordData,
                           implementation: UserKeyword,
                           result: KeywordResult):
        # Modifications to the current implementation only affect this call.
        if data.name == self.modify_once:
            implementation.body[0].name = 'Fail'
            implementation.body[0].args = ['Failed by listener once!']
            self.modify_once = None
        if not implementation.body:
            implementation.body.create_keyword('Log', ['Added by listener!'])
        # Modifications via 'owner' resource file are permanent.
        if not implementation.owner.find_keywords('Non-existing keyword'):
            kw = implementation.owner.keywords.create('Non-existing keyword')
            kw.body.create_keyword('Log', ['This keyword exists now!'])
        inv = implementation.owner.find_keywords('Invalid keyword', count=1)
        if 'fixed' not in inv.tags:
            inv.args = ['${valid}', '${args}']
            inv.tags.add('fixed')
            inv.error = None
        if implementation.matches('INVALID KEYWORD'):
            data.args = ['args modified', 'args=by listener']

    def start_invalid_keyword(self, data: KeywordData,
                              implementation: KeywordImplementation,
                              result: KeywordResult):
        if implementation.name == 'Duplicate keyword':
            assert isinstance(implementation, UserKeyword)
            implementation.error = None
            implementation.body.create_keyword('Log', ['Problem "fixed".'])
        if implementation.name == 'Non-existing keyword 2':
            assert isinstance(implementation, InvalidKeyword)
            implementation.error = None

    def start_for(self, data, result):
        data.body = []

    def start_for_iteration(self, data, result):
        # Each iteration starts with original body.
        assert not data.body
        if data.assign['${i}'] == 1:
            data.body = [{'name': 'Fail', 'args': ["Listener failed me at '${x}'!"]}]
        data.body.create_keyword('Log', ['${i}: ${x}'])

    def start_while(self, data, result):
        data.body = []

    def start_while_iteration(self, data, result):
        # Each iteration starts with original body.
        assert not data.body
        iterations = len(result.parent.body)
        name = 'Fail' if iterations == 10 else 'Log'
        data.body.create_keyword(name, [f'{name} at iteration {iterations}.'])

