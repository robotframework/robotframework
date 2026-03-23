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


def _generate_data_blocks(mdfile):
    in_block = False
    for line in mdfile.readlines():
        line = line.rstrip("\n")

        if not in_block:
            if line.strip() in ("```robotframework", "```robot"):
                in_block = True
        else:
            if line.strip() == "```":
                in_block = False
                yield ""  # Add an empty line between blocks to separate them.
            else:
                yield line


def read_markdown_data(mdfile):
    return "\n".join(_generate_data_blocks(mdfile))
