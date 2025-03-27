#!/usr/bin/env python

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

import pathlib

if __name__ == '__main__' and 'robot' not in sys.modules:
    try:
        import robot as __ignore
    except ModuleNotFoundError:
        import pythonpathsetter
        import logging
        logging.warning("depricated running without having python path setup proactively, please either install or configure python path before running __main__.py")

import robot as __ignore
assert pathlib.Path(__file__).absolute().parent() == pathlib.Path(__ignore.__file__).absolute().parent(), "you run run.py using a robot package from a different path... this is not suported"


from robot import run_cli

run_cli()
