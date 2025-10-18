import os

from robot.api.types import Secret

SECRET_VALUE = "should-not-be-logged-1234567abcd"
# A valid command that runs successfully and outputs the secret value
if os.name == 'nt':  # Windows
    SECRET_COMMAND = f'echo {SECRET_VALUE}'
else:  # Unix/Linux/Mac
    SECRET_COMMAND = f'echo {SECRET_VALUE}'


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


def verify_secret_run_command(output):
    """Verify that the command containing the secret was executed and returned output."""
    # The output should contain the secret value since the command echoes it
    assert SECRET_VALUE in output.strip(), (
        f"Expected output to contain '{SECRET_VALUE}', but got: {output!r}"
    )


def get_variables():
    return {
        "SECRET_VAR": Secret(SECRET_VALUE),
        "SECRET_COMMAND": Secret(SECRET_COMMAND),
        "SECRET_VALUE_STR": SECRET_VALUE
    }
