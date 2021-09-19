from robot.model import SuiteVisitor


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
            suite.tests.create(**dict(conf.split('-', 1) for conf in config[1:]))
            self.config = []
        elif config == ('REMOVE', 'ALL', 'TESTS'):
            suite.tests = []
        else:
            suite.tests = [t for t in suite.tests if not t.tags.match('fail')]

    def start_test(self, test):
        test.tags.add(self.config)

    def start_for(self, for_):
        if for_.parent.name == 'FOR IN RANGE loop in test':
            for_.flavor = 'IN'
            for_.values = ['FOR', 'is', 'modified!']

    def start_for_iteration(self, iteration):
        for name, value in iteration.variables.items():
            iteration.variables[name] = value + ' (modified)'
        iteration.variables['${x}'] = 'new'

    def start_if_branch(self, branch):
        if branch.condition == "'IF' == 'WRONG'":
            branch.condition = 'True'
            # With Robot
            if not hasattr(branch, 'status'):
                branch.body[0].config(name='Log', args=['going here!'])
            # With Rebot
            elif branch.status == 'NOT RUN':
                branch.status = 'PASS'
                branch.condition = 'modified'
                branch.body[0].args = ['got here!']
