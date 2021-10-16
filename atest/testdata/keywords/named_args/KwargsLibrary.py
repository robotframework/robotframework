class KwargsLibrary:

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
