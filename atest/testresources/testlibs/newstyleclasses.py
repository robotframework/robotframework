class NewStyleClassLibrary(object):
    
    def mirror(self, arg):
        arg = list(arg)
        arg.reverse()
        return ''.join(arg)

    @property
    def property_getter(self):
        raise SystemExit('This should not be called, ever!!!')

    @property
    def _property_getter(self):
        raise SystemExit('This should not be called, ever!!!')
    

class NewStyleClassArgsLibrary(object):
    
    def __init__(self, param):
        self.get_param = lambda self: param
    

import sys
if sys.version_info[0] == 2:
    from newstyleclasses2 import MetaClassLibrary
else:
    from newstyleclasses3 import MetaClassLibrary
