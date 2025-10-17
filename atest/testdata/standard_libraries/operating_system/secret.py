from robot.api.types import Secret

SECRET_VALUE = "should-not-be-logged"

def verify_secret_content_in_file(filename):
    with open(filename) as fd:
        content = fd.read()
    assert SECRET_VALUE in content, "THe secret value is not present in the file's content"

def get_variables():
    return {"SECRET_VAR": Secret("should-not-be-logged")}

