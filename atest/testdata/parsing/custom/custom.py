import re

from robot.api import TestSuite


EXTENSION = 'CUSTOM'
extension = 'ignored'


def parse(source):
    suite = TestSuite(source=source, metadata={'Parser': 'Custom'})
    for line in source.read_text().splitlines():
        if not line or line[0] in ('*', '#'):
            continue
        if line[0] != ' ':
            suite.tests.create(name=line)
        else:
            name, *args = re.split(r'\s{2,}', line.strip())
            suite.tests[-1].body.create_keyword(name, args)
    return suite
