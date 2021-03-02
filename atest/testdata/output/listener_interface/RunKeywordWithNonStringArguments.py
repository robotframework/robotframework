from robot.libraries.BuiltIn import BuiltIn


def run_keyword_with_non_string_arguments():
    return BuiltIn().run_keyword('Create List', 1, 2, None)
