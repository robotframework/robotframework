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
        if for_.parent.name == 'For In Range Loop In Test':
            for_.flavor = 'IN'
            for_.values = ['FOR', 'is', 'modified!']

    def start_if(self, if_):
        if if_.condition == "'IF' == 'WRONG'":
            if_.condition = 'True'
            if_.body[0].config(name='Log', args=['going here!'])
