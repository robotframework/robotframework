from robot import result, running
from robot.api.interfaces import ListenerV3


class Object:

    def __init__(self, attr):
        self.attr = attr

    def __str__(self):
        return f'Object({self.attr!r})'


class ArgumentModifier(ListenerV3):

    def start_library_keyword(self, data: running.Keyword,
                              implementation: running.LibraryKeyword,
                              result: result.Keyword):
        if ('modified' in data.parent.tags
                or not isinstance(data.parent, running.TestCase)):
            return

        test = data.parent.name
        create_keyword = data.parent.body.create_keyword
        data.parent.tags.add('modified')
        result.parent.tags.add('robot:continue-on-failure')

        # Modify arguments.
        if test == 'Library keyword arguments':
            implementation.owner.instance.state = 'new'
            # Need to modify both data and result with the current keyword.
            data.args = result.args = ['${STATE}', 'number=${123}', 'obj=None',
                                       r'escape=c:\\temp\\new']
            # When adding a new keyword, we only need to care about data.
            create_keyword('Library keyword', ['new', '123', r'c:\\temp\\new', 'NONE'])
            # RF 7.1 and newer support named arguments directly.
            create_keyword('Library keyword', args=['new'],
                           named_args={'number': '${42}', 'escape': r'c:\\temp\\new',
                                       'obj': Object(42)})
            create_keyword('Library keyword',
                           named_args={'number': 1.0, 'escape': r'c:\\temp\\new',
                                       'obj': Object(1), 'state': 'new'})
            create_keyword('Non-existing', args=['p'], named_args={'n': 1})

        # Test that modified arguments are validated.
        if test == 'Too many arguments':
            data.args = result.args = list('abcdefg')
            create_keyword('Library keyword', list(range(100)))
        if test == 'Conversion error':
            data.args = result.args = ['whatever', 'not a number']
            create_keyword('Library keyword', ['number=bad'])
        if test == 'Positional after named':
            data.args = result.args = ['positional', 'number=-1', 'ooops']

    def start_user_keyword(self, data: running.Keyword,
                           implementation: running.UserKeyword,
                           result: result.Keyword):

        if data.parent.name == 'User keyword arguments' and len(data.parent.body) == 1:
            data.args = result.args = ['A', 'B', 'C', 'D']
            data.parent.body.create_keyword('User keyword', ['A', 'B'],
                                            {'d': 'D', 'c': '${{"c".upper()}}'})

        if data.parent.name == 'Too many arguments':
            data.args = result.args = list('abcdefg')
