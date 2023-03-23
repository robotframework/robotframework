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
import sys

if sys.version_info < (3, 10) and not os.path.exists(__file__):
    # Try importlib resources backport as prior to python 3.10
    # importlib.resources.files was not zipapp compatible...
    try:
        from importlib_resources import files
    except ImportError:
        raise ImportError("robotframework outside of filesystem (zipapp?) requires importlib resources backport on python < 3.10")
else:
    try:
        from importlib.resources import files
    except ImportError:
        # python 3.8 or earlier:
        def files(modulepath):
            base_dir = pathlib.Path(__file__).parent.parent.parent
            return base_dir / modulepath.replace(".", os.sep)

class HtmlTemplate:
    def __init__(self, filename):
        module, self.filename = os.path.split(os.path.normpath(filename))
        self.module = 'robot.htmldata.' + module
        
    def __iter__(self):
        with files(self.module).joinpath(self.filename).open('r', encoding="utf-8") as f:
            for item in f:
                yield item.rstrip()
