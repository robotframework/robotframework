from robot.libraries.BuiltIn import BuiltIn


def log_debug_message():
    b = BuiltIn()
    b.set_log_level('DEBUG')
    b.log('Hello, debug world!', 'DEBUG')


def get_test_name():
    return BuiltIn().get_variables()['${TEST NAME}']


def set_secret_variable():
    BuiltIn().set_test_variable('${SECRET}', '*****')


def use_run_keyword_with_non_unicode_values():
    BuiltIn().run_keyword('Log', 42)
    BuiltIn().run_keyword('Log', b'\xff')


def user_keyword_via_run_keyword():
    BuiltIn().run_keyword("UseBuiltInResource.Keyword", 'This is x', 911)
