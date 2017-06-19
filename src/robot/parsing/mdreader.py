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
r'''
A Test Case TextReader for markdown files
    Robot Test Case file in markdown files (*.md) parsing support
    Original Contributor: https://gist.github.com/Tset-Noitamotua
    Any text in a markdown file within textblock that starts  with
    ```robotframework and ends with ``` in a separate line is treated as a
    valid robot script block
    for example a file testme.md contains the following markdown content
    with valid robotframework test script containing a single test case :
    # Introduction
    This is an example markdown text
    ## Script Example
    ```robotframework
    *** Test Cases ***
    My Test
        Log hello world from markdown    console=yes
    ```
    ## Some more documentation
'''
from io import BytesIO
from io import StringIO

from .txtreader import TxtReader


def MarkDownReader():
    class MarkDownReader(object):
        def __init__(self):
            self.robot_lines = []
            self.robot_data = ''

        def robotize(self, md_file):
            f = StringIO(md_file.read().decode('UTF-8'))
            try:
                include_line = False
                for line in f.readlines():
                    if not include_line:
                        include_line = (line.strip().lower() ==
                                        "```robotframework")
                    elif line.strip() == "```":
                        include_line = False
                    else:
                        self.robot_lines.append(line)
                self.robot_data = str(''.join(self.robot_lines))
            finally:
                f.close()
                return self.robot_data

        def read(self, md_file, rawdata):
            return self._read_text(self.robotize(md_file), rawdata)

        def _read_text(self, data, rawdata):
            txtfile = BytesIO(data.encode('UTF-8'))
            return TxtReader().read(txtfile, rawdata)

    return MarkDownReader()
