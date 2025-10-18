from robot.api.types import Secret

SECRET_ENV_VALUE = "secret-env-value-123"
SECRET_STDIN_VALUE = "secret-stdin-content-xyz"

def get_variables():
    return {
        "SECRET_ENV_VALUE": Secret(SECRET_ENV_VALUE),
        "SECRET_STDIN_VALUE": Secret(SECRET_STDIN_VALUE),
        "SECRET_ENV_VALUE_STR": SECRET_ENV_VALUE,
        "SECRET_STDIN_VALUE_STR": SECRET_STDIN_VALUE
    }
