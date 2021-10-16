KEYWORDS = [('other than strings', [1, 2]),
            ('named args before positional', ['a=1', 'b']),
            ('multiple varargs', ['*first', '*second']),
            ('kwargs before positional args', ['**kwargs', 'a']),
            ('kwargs before named args', ['**kwargs', 'a=1']),
            ('kwargs before varargs', ['**kwargs', '*varargs']),
            ('empty tuple', ['arg', ()]),
            ('too long tuple', [('too', 'long', 'tuple')]),
            ('too long tuple with *varargs', [('*too', 'long')]),
            ('too long tuple with **kwargs', [('**too', 'long')]),
            ('tuple with non-string first value', [(None,)]),
            ('valid argspec', ['a']),
            ('valid argspec with tuple', [['a'], ('b', None)])]


class InvalidArgSpecs:

    def get_keyword_names(self):
        return [name for name, _ in KEYWORDS]

    def run_keyword(self, name, args, kwargs):
        return ' '.join(args + tuple(kwargs)).upper()

    def get_keyword_arguments(self, name):
        return dict(KEYWORDS)[name]
