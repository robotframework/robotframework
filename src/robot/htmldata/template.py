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

import sys
from collections.abc import Iterable
from os.path import normpath
from pathlib import Path


if sys.version_info < (3, 9) and not Path(__file__).exists():    # zipsafe
    try:
        from importlib_resources import files
    except ImportError:
        raise ImportError(
            "'importlib_resources' backport module needs to be installed with "
            "Python 3.8 when Robot Framework is distributed as a zip package "
            "or '__file__' does not exist for other reasons."
        )
else:
    try:
        from importlib.resources import files
    except ImportError:    # Python 3.8
        BASE_DIR = Path(__file__).absolute().parent.parent.parent    # zipsafe

        def files(module):
            return BASE_DIR / module.replace('.', '/')


class HtmlTemplate(Iterable):

    def __init__(self, path: 'Path|str'):
        # Need to use `os.path.normpath` because `Path` does not support
        # normalizing only `..` components.
        path = Path(normpath(path))
        try:
            module, self.name = path.parts
        except ValueError:
            raise ValueError(f"HTML template path must contain only directory and "
                             f"file names like 'rebot/log.html', got '{path}'.")
        self.module = 'robot.htmldata.' + module

    def __iter__(self):
        path = files(self.module).joinpath(self.name)
        # Workaround for a bug on Windows with Python 3.9 when packaged to a zip:
        # https://github.com/python/importlib_resources/issues/281
        if hasattr(path, 'at') and '\\' in path.at:
            path.at = path.at.replace('\\', '/')
        with path.open(encoding='UTF-8') as file:
            for item in file:
                yield item.rstrip()
