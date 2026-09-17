def in_exception():
    raise RuntimeError(b"hyv\xe4")


def in_return_value():
    return b"ty\xf6paikka"


def in_message():
    print(b"\xe4iti")


def in_multiline_message():
    print(b"\xe4iti\nis\xe4")
