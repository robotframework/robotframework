from os.path import join, abspath

__all__ = ['join_with_execdir', 'abspath', 'attr_is_not_kw',
           '_not_kw_even_if_listed_in_all', 'extra stuff', None]

def join_with_execdir(arg):
    return join(abspath('.'), arg)

def not_in_all():
    pass

attr_is_not_kw = 'Listed in __all__ but not a fuction'

def _not_kw_even_if_listed_in_all():
    print('Listed in __all__ but starts with an underscore')
