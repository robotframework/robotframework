from robot.libraries.BuiltIn import BuiltIn

BIN = BuiltIn()


def start_keyword(*args):
    if BIN.get_variables()['${TESTNAME}'] == 'Listener Using BuiltIn':
        BIN.set_test_variable('${SET BY LISTENER}', 'quux')
