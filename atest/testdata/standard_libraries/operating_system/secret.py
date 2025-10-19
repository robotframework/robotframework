import os

from robot.api.types import Secret
from robot.libraries.BuiltIn import BuiltIn

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
        "The environment variable doesn't contain the secret value "
        f"(instead it is set to {os.environ[varname]})"
    )

def verify_secret_run_command(output):
    """Verify that the command containing the secret was executed and returned output."""
    # The output should contain the secret value since the command echoes it
    assert str(len(SECRET_VALUE)) in output.strip(), (
        f"Expected output to contain '{len(SECRET_VALUE)}', but got: {output!r}"
    )


def get_variables():
    progname = BuiltIn().get_variable_value("${PROG}")
    assert progname, "expected robot variable ${PROG} to be set"
    SECRET_COMMAND = f"{progname} 42 {len(SECRET_VALUE)}"

    return {
        "SECRET_VAR": Secret(SECRET_VALUE),
        "SECRET_COMMAND": Secret(SECRET_COMMAND),
        "SECRET_VALUE_STR": SECRET_VALUE
    }
