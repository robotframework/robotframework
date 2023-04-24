from pathlib import Path

from robot.api import TestSuite
from robot.api.interfaces import Defaults, Parser

import custom


class CustomParser(Parser):

    def __init__(self, extension='custom', parse=True, init=False, fail=False,
                 bad_return=False):
        print(extension)
        self.extension = extension.split(',') if extension else None
        if not parse:
            self.parse = None
        if init:
            self.extension.append('init')
        else:
            self.parse_init = None
        self.fail = fail
        self.bad_return = bad_return

    def parse(self, source: Path, defaults: Defaults) -> TestSuite:
        if self.fail:
            raise TypeError('Ooops!')
        if self.bad_return:
            return 'bad'
        return custom.parse(source, defaults)

    def parse_init(self, source: Path, defaults: Defaults) -> TestSuite:
        if self.fail:
            raise TypeError('Ooops in init!')
        if self.bad_return:
            return 42
        return TestSuite(name='📁', source=source.parent, metadata={'Parser': 'Custom'})
