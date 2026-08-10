from robot.libraries.BuiltIn import BuiltIn


def start_keyword(data, result):
    if BuiltIn().get_variables()["${TESTNAME}"] == "Listener Using BuiltIn":
        BuiltIn().set_test_variable("${SET BY LISTENER}", "quux")
