class MyObject:

    def __init__(self):
        self.args = None

    def my_method(self, *args):
        if args == ('FAIL!',):
            raise RuntimeError('Expected failure')
        self.args = args

    def kwargs(self, arg1, arg2='default', **kwargs):
        kwargs = ['%s: %s' % item for item in sorted(kwargs.items())]
        return ', '.join([arg1, arg2] + kwargs)

    def __str__(self):
        return 'String presentation of MyObject'


obj = MyObject()
