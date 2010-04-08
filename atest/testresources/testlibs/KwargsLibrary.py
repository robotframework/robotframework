class KwargsLibrary(object):

    def __init__(self, arg1=None, arg2=None):
        self.arg1 = arg1
        self.arg2 = arg2

    def check_init_arguments(self, exp_arg1, exp_arg2):
        if self.arg1 != exp_arg1 or self.arg2 != exp_arg2:
            raise AssertionError('Wrong initialization values: %s, %s'
                                 % (self.arg1, self.arg2))

    def one_kwarg(self, foo=None):
        return 'foo=%s' % foo

    def two_kwargs(self, fst=None, snd=None):
        return 'fst=%s, snd=%s' % (fst, snd)

    def four_kwargs(self, a=None, b=None, c=None, d=None):
        return 'a=%s, b=%s, c=%s, d=%s' % (a, b, c, d)

    def mandatory_and_kwargs(self, a, b, c=None):
        return 'a=%s, b=%s, c=%s' % (a, b, c)

    def kwargs_and_mandatory_args(self, mandatory, d1=None, d2=None, *varargs):
        return 'mandatory=%s, d1=%s, d2=%s, varargs=%s' \
                % (mandatory, d1, d2, '[%s]' % ','.join(varargs))