from robot.libraries.BuiltIn import BuiltIn


def my_run_keyword(name, *args):
    return BuiltIn().run_keyword(name, *args)