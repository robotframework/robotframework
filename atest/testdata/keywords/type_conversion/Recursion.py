type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None


def create_nested_list(depth: int) -> list:
    value = [1]
    for _ in range(depth - 1):
        value = [value]
    return value


def validate_list(data: JSON):
    print(data)
    while isinstance(data, list):
        data = data[0]
    if data != 1:
        raise AssertionError(f"Expected leaf value to be 1, got {data!r}.")
