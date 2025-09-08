from typing import TypedDict

from robot.api import Secret


class Credential(TypedDict):
    username: str
    password: Secret


def library_get_secret(value: str = "This is a secret") -> Secret:
    return Secret(value)


def library_not_secret():
    return "This is a string, not a secret"


def library_receive_secret(secret: Secret) -> str:
    return secret.value


def library_receive_credential(credential: Credential) -> str:
    return (
        f"Username: {credential['username']}, Password: {credential['password'].value}"
    )


def library_list_of_secrets(secrets: "list[Secret]") -> str:
    return ", ".join(secret.value for secret in secrets)


def get_variables():
    return {
        "VAR_FILE": Secret("From variable file"),
        "VAR_FILE_SECRET": Secret("This is a secret used in tests"),
    }
