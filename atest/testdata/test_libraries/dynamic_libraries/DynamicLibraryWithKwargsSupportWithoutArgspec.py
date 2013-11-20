import sys
import os

# TODO: 1) Is sys.path.insert really needed?
# TODO: 2) Should not update KEYWORDS without copying it first.
# TODO: 3) See also DynamicLibraryWithoutArgspec

sys.path.insert(0, os.path.dirname(__file__))
from DynamicLibraryWithoutArgspec import (
  KEYWORDS, DynamicLibraryWithoutArgspec)


def do_something_with_kwargs(a, b=2, c=3, **kwargs):
    print a, b, c, ' '.join('%s:%s' % (k, v) for k, v in kwargs.items())

KEYWORDS.update({
    'do_something_with_kwargs': do_something_with_kwargs,
})

class DynamicLibraryWithKwargsSupportWithoutArgspec(DynamicLibraryWithoutArgspec):

    def run_keyword(self, kw_name, args, kwargs):
        return KEYWORDS[kw_name](*args, **kwargs)
