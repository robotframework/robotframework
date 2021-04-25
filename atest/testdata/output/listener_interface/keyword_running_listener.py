ROBOT_LISTENER_API_VERSION = 2


from robot.libraries.BuiltIn import BuiltIn

run_keyword = BuiltIn().run_keyword


def start_suite(name, attrs):
    run_keyword('Log', 'start_suite')


def end_suite(name, attrs):
    run_keyword('Log', 'end_suite')


def start_test(name, attrs):
    run_keyword('Log', 'start_test')


def end_test(name, attrs):
    run_keyword('Log', 'end_test')


def start_keyword(name, attrs):
    run_keyword('Log', 'start_keyword')


def end_keyword(name, attrs):
    run_keyword('Log', 'end_keyword')
