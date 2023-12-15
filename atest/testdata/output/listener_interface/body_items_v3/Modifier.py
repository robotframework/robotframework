from robot import result, running


class Modifier:
    modify_once = 'User keyword'

    def start_library_keyword(self, data: running.Keyword,
                              implementation: running.LibraryKeyword,
                              result: result.Keyword):
        if (isinstance(data.parent, running.TestCase)
                and data.parent.name == 'Library keyword'):
            implementation.owner.instance.state = 'set by listener'

    def start_user_keyword(self, data: running.Keyword,
                           implementation: running.UserKeyword,
                           result: result.Keyword):
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
            result.args = ['${secret}']
            result.doc = 'Results can be modified!'
            result.tags.add('start')

    def end_keyword(self, data: running.Keyword, result: result.Keyword):
        if 'start' in result.tags:
            result.tags.add('end')
            result.doc = result.doc[:-1] + ' both in start and end!'

    def start_invalid_keyword(self, data: running.Keyword,
                              implementation: running.KeywordImplementation,
                              result: result.Keyword):
        if implementation.name == 'Duplicate keyword':
            assert isinstance(implementation, running.UserKeyword)
            implementation.error = None
            implementation.body.create_keyword('Log', ['Problem "fixed".'])
        if implementation.name == 'Non-existing keyword 2':
            assert isinstance(implementation, running.InvalidKeyword)
            implementation.error = None

    def start_for(self, data: running.For, result: result.For):
        data.body.clear()
        result.assign = ['secret']

    def start_for_iteration(self, data: running.ForIteration,
                            result: result.ForIteration):
        # Each iteration starts with original body.
        assert not data.body
        if data.assign['${i}'] == 1:
            data.body = [{'name': 'Fail', 'args': ["Listener failed me at '${x}'!"]}]
        data.body.create_keyword('Log', ['${i}: ${x}'])
        result.assign['${x}'] = 'xxx'

    def start_while(self, data: running.While, result: result.While):
        data.body.clear()

    def start_while_iteration(self, data: running.WhileIteration,
                              result: result.WhileIteration):
        # Each iteration starts with original body.
        assert not data.body
        iterations = len(result.parent.body)
        name = 'Fail' if iterations == 10 else 'Log'
        data.body.create_keyword(name, [f'{name} at iteration {iterations}.'])

    def start_if(self, data: running.If, result: result.If):
        data.body[1].condition = 'False'
        data.body[2].body[0].args = ['Executed!']

    def start_if_branch(self, data: running.IfBranch, result: result.IfBranch):
        if data.type == data.ELSE:
            assert result.status == result.NOT_SET
        else:
            assert result.status == result.NOT_RUN
        result.message = 'Secret message!'

    def start_try(self, data: running.Try, result: result.Try):
        data.body[0].body[0].args = ['Not caught!']
        data.body[1].patterns = ['No match!']
        data.body.pop()

    def start_try_branch(self, data: running.TryBranch, result: result.TryBranch):
        assert data.type != data.FINALLY

    def start_var(self, data: running.Var, result: result.Var):
        if data.name == '${y}':
            data.value = 'VAR by listener'
        result.value = ['secret']

    def start_return(self, data: running.Return, result: running.Return):
        data.values = ['RETURN by listener']

    def end_return(self, data: running.Return, result: running.Return):
        result.values = ['secret']
