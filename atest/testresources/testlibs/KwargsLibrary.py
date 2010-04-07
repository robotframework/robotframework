class KwargsLibrary(object):

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