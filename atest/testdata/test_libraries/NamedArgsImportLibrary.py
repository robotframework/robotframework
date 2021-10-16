class NamedArgsImportLibrary:

    def __init__(self, arg1=None, arg2=None, **kws):
        self.arg1 = arg1
        self.arg2 = arg2
        self.kws = kws

    def check_init_arguments(self, exp_arg1, exp_arg2, **kws):
        if self.arg1 != exp_arg1 or self.arg2 != exp_arg2 or kws != self.kws:
            raise AssertionError('Wrong initialization values. Got (%s, %s, %r), expected (%s, %s, %r)'
                                 % (self.arg1, self.arg2, self.kws, exp_arg1, exp_arg2, kws))
