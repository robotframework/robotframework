def end_keyword(data, result):
    if result.failed and result.message == "Pass me!":
        result.passed = True
        result.message = "Failure hidden!"
    elif result.passed and "Fail me!" in result.args:
        result.failed = True
        result.message = "Ooops!!"
    elif result.passed and "Silent fail!" in result.args:
        result.failed = True
    elif result.skipped:
        result.failed = True
        result.message = "Failing!"
    elif result.message == "Skip me!":
        result.skipped = True
        result.message = "Skipping!"
    elif result.not_run and "Fail me!" in result.args:
        result.failed = True
        result.message = "Failing without running!"
    elif "Mark not run!" in result.args:
        result.not_run = True
    elif result.message == "Change me!" or result.name == "Change message":
        result.message = "Changed!"


def end_structure(data, result):
    result.passed = True


end_for = end_while = end_if = end_try = end_structure
