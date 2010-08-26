#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
from robot import runner, run_from_cli, rebot, rebot_from_cli


class JarRunner(RobotRunner):
    """Used for Java-Jython interop when RF is executed from .jar file"""

    def run(self, args):
        try:
            if args and args[0] == 'rebot':
                rebot_from_cli(args[1:], rebot.__doc__)
            else:
                run_from_cli(args, runner.__doc__)
        except SystemExit, err:
            return err.code

