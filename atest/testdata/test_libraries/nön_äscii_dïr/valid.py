def keyword_in_non_ascii_dir():
    return "Keyword in 'nön_äscii_dïr'!"


def failing_keyword_in_non_ascii_dir():
    raise AssertionError("Keyword in 'nön_äscii_dïr' fails!")
