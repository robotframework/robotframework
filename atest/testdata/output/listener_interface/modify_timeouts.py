from robot.libraries.BuiltIn import BuiltIn


def start_test(data, result):
    if data.name in ("Add test timeout", "Shorten test timeout", "Timeout in setup"):
        data.timeout = "100 milliseconds"
    elif data.name == "Extend test timeout":
        data.timeout = "1 minute"
    elif data.name == "Remove test timeout":
        data.timeout = None
    elif data.name == "Disable test timeout":
        data.timeout = "NONE"
    elif data.name == "Timeout from listener variable":
        BuiltIn().set_test_variable("${LISTENER TIMEOUT}", "100 milliseconds")
        data.timeout = "${LISTENER TIMEOUT}"
    elif data.name == "Invalid timeout from listener":
        data.timeout = "invalid"


def start_user_keyword(data, implementation, result):
    if data.name == "Add keyword timeout":
        implementation.timeout = "100 milliseconds"
    elif data.name == "Remove keyword timeout":
        implementation.timeout = None
