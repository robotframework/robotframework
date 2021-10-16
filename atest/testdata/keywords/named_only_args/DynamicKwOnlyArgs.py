class DynamicKwOnlyArgs:
    keywords = {
        'Args Should Have Been': ['*args', '**kwargs'],
        'Kw Only Arg': ['*', 'kwo'],
        'Many Kw Only Args': ['*', 'first', 'second', 'third'],
        'Kw Only Arg With Default': ['*', 'kwo=default', 'another=another'],
        'Mandatory After Defaults': ['*', 'default1=xxx', 'mandatory', 'default2=zzz'],
        'Kw Only Arg With Varargs': ['*varargs', 'kwo'],
        'All Arg Types': ['pos_req', 'pos_def=pd', '*varargs',
                          'kwo_req', 'kwo_def=kd', '**kwargs']
    }

    def __init__(self):
        self.args = self.kwargs = None

    def get_keyword_names(self):
        return list(self.keywords)

    def get_keyword_arguments(self, name):
        return self.keywords[name]

    def run_keyword(self, name, args, kwargs):
        if name != 'Args Should Have Been':
            self.args = args
            self.kwargs = kwargs
        elif self.args != args:
            raise AssertionError("Expected arguments %s, got %s."
                                 % (args, self.args))
        elif self.kwargs != kwargs:
            raise AssertionError("Expected kwargs %s, got %s."
                                 % (kwargs, self.kwargs))
