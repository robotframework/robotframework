from robot.libraries.BuiltIn import BuiltIn

def get_result_or_error(*args):
    try:
        return BuiltIn().run_keyword(*args)
    except Exception, err:
        return err.message

def pretty(*args):
    return ', '.join(args)
