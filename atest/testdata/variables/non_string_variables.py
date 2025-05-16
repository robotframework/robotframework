import sys


def get_variables():
    variables = {
        "integer": 42,
        "float": 3.14,
        "bytes": b"hyv\xe4",
        "bytearray": bytearray(b"hyv\xe4"),
        "low_bytes": b"\x00\x01\x02",
        "boolean": True,
        "none": None,
        "module": sys,
        "module_str": str(sys),
        "list": [1, b"\xe4", "\xe4"],
        "dict": {b"\xe4": "\xe4"},
        "list_str": "[1, b'\\xe4', '\xe4']",
        "dict_str": "{b'\\xe4': '\xe4'}",
    }
    return variables
