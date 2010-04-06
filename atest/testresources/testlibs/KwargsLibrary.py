class KwargsLibrary(object):

    def onekwarg(self, foo=None):
        return 'foo=%s' % foo

    def twokwargs(self, fst=None, snd=None):
        return 'fst=%s, snd=%s' % (fst, snd)

    def fourkwargs(self, a=None, b=None, c=None, d=None):
        return 'a=%s, b=%s, c=%s, d=%s' % (a, b, c, d)

