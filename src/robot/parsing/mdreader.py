#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
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
from io import BytesIO
from io import StringIO

from robot.utils import Utf8Reader
from .txtreader import TxtReader


def MarkDownReader():
    class MarkDownReader(object):
        def __init__(self):
            self.robot_lines = []
            self.robot_data = ''

        def robotize(self, md_file):
            try:
                include_line = False
                for line in Utf8Reader(md_file).readlines():
                    if not include_line:
                        include_line = (line.strip().lower() ==
                                        "```robotframework")
                    elif line.strip() == "```":
                        include_line = False
                    else:
                        self.robot_lines.append(line)
                self.robot_data = ''.join(self.robot_lines)
            finally:
                return self.robot_data

        def read(self, md_file, rawdata):
            return self._read_text(self.robotize(md_file), rawdata)

        def _read_text(self, data, rawdata):
            txtfile = BytesIO(data.encode('UTF-8'))
            return TxtReader().read(txtfile, rawdata)

    return MarkDownReader()
