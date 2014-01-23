#  Copyright 2008-2014 Nokia Solutions and Networks
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from org.robotframework import RobotRunner
from robot import run_cli, rebot_cli
from robot.libdoc import libdoc_cli
from robot.tidy import tidy_cli
from robot.testdoc import testdoc_cli


USAGE = """robotframework.jar - Robot Framework runner.

Usage: java -jar robotframework.jar [command] [options] [input(s)]

Available commands:
  run     - Run Robot Framework tests. The default, if no command is given.
  rebot   - Post process Robot Framework output files.
  libdoc  - Create test library or resource file documentation.
  tidy    - Clean-up and changed format of test data files.
  testdoc - Create documentation from Robot Framework test data files.

Run `java -jar robotframework.jar command --help` for more information about
an individual command.

Examples:
  java -jar robotframework.jar mytests.txt
  java -jar robotframework.jar run mytests.txt
  java -jar robotframework.jar rebot --log mylog.html out.xml
  java -jar robotframework.jar tidy --format txt mytests.html
"""


class JarRunner(RobotRunner):
    """Used for Java-Jython interop when RF is executed from .jar file"""
    _commands = {'run': run_cli, 'rebot': rebot_cli, 'tidy': tidy_cli,
                 'libdoc': libdoc_cli, 'testdoc': testdoc_cli}

    def run(self, args):
        try:
            self._run(args)
        except SystemExit, err:
            return err.code

    def _run(self, args):
        if not args or args[0] in ('-h', '--help'):
            print USAGE
            raise SystemExit(0)
        command, args = self._parse_command_line(args)
        command(args) # Always calls sys.exit()

    def _parse_command_line(self, args):
        try:
            return self._commands[args[0]], args[1:]
        except KeyError:
            return run_cli, args
