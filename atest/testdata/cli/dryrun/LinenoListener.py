def start_keyword(data, result):
    if not isinstance(data.lineno, int):
        raise ValueError(f"lineno should be int, got {type(data.lineno)}")
    result.doc = f"Keyword {data.name!r} on line {data.lineno}."


def end_keyword(data, result):
    if not isinstance(data.lineno, int):
        raise ValueError(f"lineno should be int, got {type(data.lineno)}")
