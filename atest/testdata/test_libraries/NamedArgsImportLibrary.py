class NamedArgsImportLibrary:

    def __init__(self, arg1=None, arg2=None, **kws):
        self.arg1 = arg1
        self.arg2 = arg2
        self.kws = kws

    def check_init_arguments(self, arg1, arg2, **kws):
        if self.arg1 != arg1 or self.arg2 != arg2 or kws != self.kws:
            raise AssertionError(
                f"Wrong initialization values. "
                f"Got ({self.arg1!r}, {self.arg2!r}, {self.kws!r}), "
                f"expected ({arg1!r}, {arg2!r}, {kws!r})"
            )
