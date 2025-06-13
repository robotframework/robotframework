from robot.utils import Secret


def library_get_secret(value: str = "This is a secret") -> Secret:
    return Secret(value)


def library_not_secret():
    return "This is a string, not a secret"


def library_receive_secret(secret: Secret) -> str:
    return secret.value


def get_variables():
    return {"VAR_FILE": Secret("From variable file")}
