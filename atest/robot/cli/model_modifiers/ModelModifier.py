from robot.model import SuiteVisitor
from robot.running.model import Argument


class ModelModifier(SuiteVisitor):

    def __init__(self, *tags, **extra):
        if extra:
            tags += tuple('%s-%s' % item for item in extra.items())
        self.config = tags or ('visited',)

    def start_suite(self, suite):
        config = self.config
        if config[0] == 'FAIL':
            raise RuntimeError(' '.join(self.config[1:]))
        elif config[0] == 'CREATE':
            tc = suite.tests.create(**dict(conf.split('-', 1) for conf in config[1:]))
            tc.body.create_keyword('Log', args=['Hello', 'level=INFO'])
            # robot.running.model.Argument is a private/temporary API for creating
            # named arguments with non-string values programmatically. It was added
            # in RF 7.0.1 (#5031) after a failed attempt to add an API for this
            # purpose in RF 7.0 (#5000). A better, public API is planned for RF 7.1.
            tc.body.create_keyword('Log', args=[Argument(None, 'Argument object!'),
                                                Argument('level', 'INFO')])
            tc.body.create_keyword('Should Contain', args=[(1, 2, 3),
                                                           Argument('item', 2)])
            self.config = []
        elif config == ('REMOVE', 'ALL', 'TESTS'):
            suite.tests = []
        else:
            suite.tests = [t for t in suite.tests if not t.tags.match('fail')]

    def start_test(self, test):
        self.make_non_empty(test, 'Test')
        if hasattr(test.parent, 'resource'):
            for kw in test.parent.resource.keywords:
                self.make_non_empty(kw, 'Keyword')
        test.tags.add(self.config)

    def make_non_empty(self, item, kind):
        if not item.name:
            item.name = f'{kind} name made non-empty by modifier'
            item.body.clear()
        if not item.body:
            item.body.create_keyword('Log', [f'{kind} body made non-empty by modifier'])

    def start_for(self, for_):
        if for_.parent.name == 'FOR IN RANGE':
            for_.flavor = 'IN'
            for_.values = ['FOR', 'is', 'modified!']

    def start_for_iteration(self, iteration):
        for name, value in iteration.assign.items():
            iteration.assign[name] = value + ' (modified)'
        iteration.assign['${x}'] = 'new'

    def start_if_branch(self, branch):
        if branch.condition == "'${x}' == 'wrong'":
            branch.condition = 'True'
            # With Robot
            if not hasattr(branch, 'status'):
                branch.body[0].config(name='Log', args=['going here!'])
            # With Rebot
            elif branch.status == 'NOT RUN':
                branch.status = 'PASS'
                branch.condition = 'modified'
                branch.body[0].args = ['got here!']
        if branch.condition == '${i} == 9':
            branch.condition = 'False'
