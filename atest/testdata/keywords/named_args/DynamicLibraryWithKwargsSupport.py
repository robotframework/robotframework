from DynamicLibrary import KEYWORDS, DynamicLibrary

class DynamicLibraryWithKwargsSupport(DynamicLibrary):

    def run_keyword(self, kw_name, args, kwargs):
        return KEYWORDS[kw_name][0](*args, **kwargs)
