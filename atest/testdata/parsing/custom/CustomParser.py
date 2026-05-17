from pathlib import Path

import custom

from robot.api import TestSuite
from robot.api.interfaces import Parser, TestDefaults
from robot.running.resourcemodel import ResourceFile

# TODO: Move ResourceFile to `robot.api`?


class CustomParser(Parser):
    def __init__(
        self,
        extension="custom",
        parse=True,
        init=False,
        resource=False,
        fail=False,
        bad_return=False,
    ):
        self.extension = extension.split(",") if extension else None
        if not parse:
            self.parse = None

        if init:
            self.extension.append("init")
        else:
            self.parse_init = None

        if resource:
            self.extension.append("resource")
        else:
            self.parse_resource = None

        self.fail = fail
        self.bad_return = bad_return

    def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
        if self.fail:
            raise TypeError("Ooops!")
        if self.bad_return:
            return "bad"
        suite = custom.parse(source)
        suite.name = TestSuite.name_from_source(source, self.extension)
        for test in suite.tests:
            defaults.set_to(test)
        return suite

    def parse_init(self, source: Path, defaults: TestDefaults) -> TestSuite:
        if self.fail:
            raise TypeError("Ooops in init!")
        if self.bad_return:
            return 42
        defaults.tags = ["tag from init"]
        defaults.setup = {"name": "Log", "args": ["setup from init"]}
        defaults.teardown = {"name": "Log", "args": ["teardown from init"]}
        defaults.timeout = "42s"
        return TestSuite(name="📁", source=source.parent, metadata={"Parser": "Custom"})

    def parse_resource(self, source: Path) -> ResourceFile:
        if self.fail:
            raise TypeError("Ooops in resource!")
        if self.bad_return:
            return True
        return ResourceFile(source=source, owner=None, doc="Pre-parsed resource file")
