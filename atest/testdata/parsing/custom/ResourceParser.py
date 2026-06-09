from pathlib import Path

from robot.api import TestSuite
from robot.api.interfaces import Parser, TestDefaults
from robot.running.model import TestCase
from robot.running.resourcemodel import ResourceFile, UserKeyword

# TODO: Move ResourceFile to `robot.api`?


class ResourceParser:
    # TODO: Make types / abstract classes work
    # class ResourceParser(Parser):
    extension = ("robot", "rbt")
    resource_extension = ("resource", "res", "TMP")

    def parse(self, source: Path, defaults: TestDefaults) -> TestSuite:
        suite = TestSuite.from_file_system(source, defaults=defaults)

        suite.tests.append(
            TestCase.from_dict(
                {
                    "name": "Test from preprocessor",
                    "lineno": 5,
                    "body": [{"name": "Keyword From Preprocessor", "lineno": 6}],
                }
            )
        )
        return suite

    def parse_resource(self, source: Path) -> ResourceFile:
        resource = ResourceFile.from_file_system(source)

        new_keyword = UserKeyword.from_dict(
            {
                "name": "Keyword From Preprocessor",
                "lineno": 10,
                "body": [{"name": "No Operation", "lineno": 11}],
            }
        )
        resource.keywords.append(new_keyword)

        return resource
