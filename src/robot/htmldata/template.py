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

import os
import pathlib
import warnings


try:
    from importlib.resources import open_text
except ImportError :
    try:
        # This code is here to optionally suport zipapps with python 3.6,
        # under the condition that the backport importlib-resources is
        # installed.
        from importlib_resources import open_text
    except ImportError:
        # use our own...

        def open_text(modulepath, resource_part, encoding='utf-8'):
            base_dir = pathlib.Path(__file__).parent.parent.parent
            resource_path = base_dir / modulepath.replace(".", os.sep) / resource_part
            return open(resource_path, "r", encoding=encoding)

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

    parts = ("." + item.replace(".", "") for item in parts)
    modulepart = "robot.htmldata" + "".join(parts)
    with warnings.catch_warnings():
        # This is necessay as open_text is deprecated started from python 
        # 3.11, but the alternatives given did create issues in zipapps...
        warnings.simplefilter("ignore")
        with open_text(modulepart, resource_name, encoding='utf-8') as f:
            for item in f:
                yield item.rstrip()
