#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
from robot.tidy import tidy_cli


class JarRunner(RobotRunner):
    """Used for Java-Jython interop when RF is executed from .jar file"""
    _progs = {
        'run': run_cli,
        'rebot': rebot_cli,
        'tidy': tidy_cli
    }

    def run(self, args):
        try:
            prog, args = self._parse_prog_and_args(args)
            return prog(args)
        except SystemExit, err:
            return err.code

    def _parse_prog_and_args(self, args):
        try:
            return self._progs[args[0]], args[1:]
        except (KeyError, IndexError):
            pass
        return run_cli, args


