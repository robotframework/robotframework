from robot.libraries.BuiltIn import BuiltIn, register_run_keyword


def run_keyword_function(name, *args):
    return BuiltIn().run_keyword(name, *args)


register_run_keyword(__name__, 'run_keyword_function', 1)

def run_keyword_without_keyword(*args):
    return BuiltIn().run_keyword('\Log Many', *args)

register_run_keyword(__name__, 'run_keyword_without_keyword', 0)
