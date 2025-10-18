import os

from robot.api.types import Secret

SECRET_VALUE = "should-not-be-logged-1234567abcd"


def verify_secret_content_in_file(filename):
    with open(filename) as fd:
        content = fd.read()
    assert SECRET_VALUE in content, (
        "The secret value is not present in the file's content"
    )


def verify_secret_in_env_var(varname, prefix=''):
    assert varname in os.environ, (
        "The environment variable is not set"

    )
    assert os.environ[varname] == prefix + SECRET_VALUE, (
        "The environment variable doesn't contain the secret value"
    )


def get_variables():
    return {"SECRET_VAR": Secret(SECRET_VALUE)}
