def annotations(arg1, arg2: str):
    return f"annotations: {arg1} {arg2}"


def annotations_with_defaults(arg1, arg2: "has a default" = "default"):  # noqa: F722
    return f"annotations: {arg1} {arg2}"
