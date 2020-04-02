# coding=UTF-8


def keyword_in_non_ascii_dir():
    return u"Keyword in 'nön_äscii_dïr'!"


def failing_keyword_in_non_ascii_dir():
    raise AssertionError(u"Keyword in 'nön_äscii_dïr' fails!")
