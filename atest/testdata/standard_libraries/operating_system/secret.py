import os

from robot.api.types import Secret

SECRET_VALUE = "should-not-be-logged"


def verify_secret_content_in_file(filename):
    with open(filename) as fd:
        content = fd.read()
    assert SECRET_VALUE in content, (
        "The secret value is not present in the file's content"
    )


def verify_secret_in_env_var(varname, prefix=""):
    expected_value = prefix + SECRET_VALUE
    assert os.environ.get(varname) == expected_value, (
        "The environment variable is not set or doesn't contain the secret value"
    )


def get_variables():
    return {"SECRET_VAR": Secret("should-not-be-logged")}
