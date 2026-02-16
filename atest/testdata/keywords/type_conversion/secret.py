from typing import Any, TypedDict

from robot.api.types import Secret


class Credential(TypedDict):
    username: str
    password: Secret


def library_get_secret(value: str = "This is a secret") -> Secret:
    return Secret(value)


def library_not_secret():
    return "This is a string, not a secret"


def library_receive_secret(secret: Secret, expected: str = "Secret value"):
    assert secret.value, expected


def library_receive_credential(credential: Credential) -> str:
    return (
        f"Username: {credential['username']}, Password: {credential['password'].value}"
    )


def library_list_of_secrets(secrets: "list[Secret]") -> str:
    return ", ".join(secret.value for secret in secrets)


def library_receive_str(arg: str) -> None:
    raise ValueError("This is should fail if called with a Secret")


def library_receive_bool(arg: bool) -> None:
    raise ValueError("This is should fail if called with a Secret")


def library_receive_any(arg: Any) -> None:
    return arg.value


def library_receive_object(arg: object) -> None:
    return arg.value


def library_receive_list_str(arg: "list[str]") -> None:
    raise ValueError("This is should fail if called with a list of Secrets")


def get_variables():
    return {"VAR_FILE": Secret("Secret value")}
