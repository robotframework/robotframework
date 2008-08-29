from robot.libraries.BuiltIn import BuiltIn, register_run_keyword


def run_keyword_function(name, *args):
    return BuiltIn().run_keyword(name, *args)


register_run_keyword(__name__, run_keyword_function)
