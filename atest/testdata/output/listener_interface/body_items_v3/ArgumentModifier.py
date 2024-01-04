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
        if 'modified' in data.parent.tags:
            return

        test = data.parent.name
        create_keyword = data.parent.body.create_keyword
        data.parent.tags.add('modified')
        result.parent.tags.add('robot:continue-on-failure')

        # Set arguments using strings. Need to handle `name=value` syntax, escaping,
        # etc. Variables are supported. Non-string arguments are accepted as-is.
        if test == 'Arguments as strings':
            # Need to modify both data and result with the current keyword.
            data.args = result.args = ['${STATE}', 'number=${123}', 'obj=None',
                                       r'escape=c:\\temp\\new']
            # When adding a new keyword, we only need to care about data.
            create_keyword('Library keyword', ['new', '123', r'c:\\temp\\new', 'NONE'])
            implementation.owner.instance.state = 'new'

        # Set arguments using tuples (and strings). With tuples named-arguments
        # are handled automatically, but escaping needs to be handled separately.
        # Variables are supported.
        if test == 'Arguments as tuples':
            data.args = result.args = [('${STATE}',), ('escape', r'c:\\temp\\new'),
                                       ('obj', Object(123)), ('number', '${123}')]
            create_keyword('Library keyword', [('new',), 1.0, ('obj', Object(1)),
                                               r'escape=c:\\temp\\new'])
            implementation.owner.instance.state = 'new'

        # Set arguments directly as a list of positional arguments and a dictionary
        # of named arguments. Variables are not supported and there's no need for
        # escaping. Argument conversion and validation is done.
        if test == 'Arguments directly as positional and named':
            data.args = result.args = (['${XXX}', '456', r'c:\temp\new'],
                                       {'obj': Object(456)})
            create_keyword('Library keyword', [(), {'state': '${XXX}', 'obj': Object(1),
                                                    'number': '1.0',
                                                    'escape': r'c:\temp\new'}])
            implementation.owner.instance.state = '${XXX}'

        # Test that modified arguments are validated.
        if test == 'Too many arguments':
            data.args = result.args = list('abcdefg')
            create_keyword('Library keyword', [list(range(100)), {}])
        if test == 'Conversion error':
            data.args = result.args = ['whatever', 'not a number']
            create_keyword('Library keyword', [(), {'number': 'bad'}])
        if test == 'Named argument not matching':
            data.args = result.args = [(), {'no': 'match'}]
            create_keyword('Library keyword', [('o', 'k'), {'bad': 'name'}])
        if test == 'Positional after named':
            data.args = result.args = [('positional',), ('name', 'value'), ('ooops',)]
