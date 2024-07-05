import os
import tempfile
from pathlib import Path


TEMPDIR = Path(os.getenv('TEMPDIR', tempfile.gettempdir()))


class LinenoAndSource:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.suite_output = self._open('LinenoAndSourceSuite.txt')
        self.test_output = self._open('LinenoAndSourceTests.txt')
        self.output = None

    def _open(self, name):
        return open(TEMPDIR / name, 'w', encoding='UTF-8')

    def start_suite(self, name, attrs):
        self.output = self.suite_output
        self.report('START', type='SUITE', name=name, **attrs)

    def end_suite(self, name, attrs):
        self.output = self.suite_output
        self.report('END',  type='SUITE', name=name, **attrs)

    def start_test(self, name, attrs):
        self.output = self.test_output
        self.report('START', type='TEST', name=name, **attrs)
        self.output = self._open(name + '.txt')

    def end_test(self, name, attrs):
        self.output.close()
        self.output = self.test_output
        self.report('END', type='TEST', name=name, **attrs)
        self.output = self.suite_output

    def start_keyword(self, name, attrs):
        self.report('START', **attrs)

    def end_keyword(self, name, attrs):
        self.report('END', **attrs)

    def close(self):
        self.suite_output.close()
        self.test_output.close()

    def report(self, event, type, source, lineno=-1, name=None, kwname=None,
               status=None, **ignore):
        info = [event, type, (name or kwname).replace('    ', ' '), lineno, source]
        if status:
            info.append(status)
        self.output.write('\t'.join(str(i) for i in info) + '\n')
