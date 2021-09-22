__all__ = ['VAR']


class Demeter(object):
    loves = ''
    @property
    def hates(self):
        return self.loves.upper()


class Variable(object):
    attr = 'value'
    _attr2 = 'v2'
    attr2 = property(lambda self: self._attr2,
                     lambda self, value: setattr(self, '_attr2', value.upper()))
    demeter = Demeter()
    @property
    def not_settable(self):
        return None


VAR = Variable()
