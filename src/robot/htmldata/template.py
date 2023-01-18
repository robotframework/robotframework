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

from os.path import abspath, dirname, join, normpath
try:
    import importlib.resources as ir
except:
    import importlib_resources as ir
import pathlib


def HtmlTemplate(filename):
    parts = pathlib.Path(filename).parts
    resource_name = parts[-1]
    parts = list(parts[:-1])

    idx = 0
    while idx < len(parts):
        if parts[idx] == "..":
            del parts[idx]
            del parts[idx-1]
            idx -= 1
        else:
            idx += 1
    parts = (item.replace(".", "") for item in parts)

    modulepart = "robot.htmldata." + ".".join(parts)
    return iter(ir.open_text(modulepart, resource_name))
