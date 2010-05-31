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


from output import Output
from logger import LOGGER
from monitor import CommandLineMonitor
from xmllogger import XmlLogger
from loggerhelper import LEVELS, Message
from readers import process_output, process_outputs


# Hooks to output. Set by Output.
# Use only if no other way available (e.g. from BuiltIn library)
OUTPUT = None


def TestSuite(outpath):
    """Factory method for getting test suite from an xml output file.

    If you want statistics get suite first and say Statistics(suite).
    """
    suite, errors = process_output(outpath)

    def write_to_file(path=None):
        """Write processed suite (incl. statistics and errors) back to xml.

        If path is not given the suite is written into the same file as it
        originally was read from.
        """
        from robot.serializing import RobotTestOutput
        if path is None:
            path = outpath
        suite.set_status()
        testoutput = RobotTestOutput(suite, errors)
        testoutput.serialize_output(path, suite)

    suite.write_to_file = write_to_file
    return suite

