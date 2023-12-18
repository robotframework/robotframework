from robot.libraries.BuiltIn import BuiltIn, register_run_keyword


def run_keyword_function(name, *args):
    return BuiltIn().run_keyword(name, *args)


def run_keyword_without_keyword(*args):
    return BuiltIn().run_keyword(r'\\Log Many', *args)


register_run_keyword(__name__, 'run_keyword_function', 1,
                     deprecation_warning=False)
register_run_keyword(__name__, 'run_keyword_without_keyword', 0,
                     deprecation_warning=False)
