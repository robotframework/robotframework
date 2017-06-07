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

"""Implements writing of parsed, and possibly edited, test data back to files.

This functionality is used by :meth:`robot.parsing.model.TestCaseFile.save`
and indirectly by :mod:`robot.tidy`. External tools should not need to use
this package directly.

This package is considered stable, although the planned changes to
:mod:`robot.parsing` may affect also this package.
"""

from .datafilewriter import DataFileWriter
