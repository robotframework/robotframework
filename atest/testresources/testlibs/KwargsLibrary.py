class KwargsLibrary(object):

    def __init__(self, arg1=None, arg2=None, **kws):
        self.arg1 = arg1
        self.arg2 = arg2
        self.kws = kws

    def check_init_arguments(self, exp_arg1, exp_arg2, **kws):
        if self.arg1 != exp_arg1 or self.arg2 != exp_arg2 or kws != self.kws:
            raise AssertionError('Wrong initialization values. Got (%s, %s, %r), expected (%s, %s, %r)'
                                 % (self.arg1, self.arg2, self.kws, exp_arg1, exp_arg2, kws))

    def one_named(self, named=None):
        return named

    def two_named(self, fst=None, snd=None):
        return '%s, %s' % (fst, snd)

    def four_named(self, a=None, b=None, c=None, d=None):
        return '%s, %s, %s, %s' % (a, b, c, d)

    def mandatory_and_named(self, a, b, c=None):
        return '%s, %s, %s' % (a, b, c)

    def mandatory_named_and_varargs(self, mandatory, d1=None, d2=None, *varargs):
        return '%s, %s, %s, %s' % (mandatory, d1, d2, '[%s]' % ', '.join(varargs))
