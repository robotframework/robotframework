#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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

"""Contains base classes and other generic functionality.

In RF 2.7 this package is mainly used by :mod:`robot.result` package, but
there is a plan to change also :mod:`robot.running` to use this in RF 2.8.

This package is considered stable.
"""

from .testsuite import TestSuite
from .testcase import TestCase
from .keyword import Keyword
from .message import Message
from .tags import Tags, TagPatterns
from .criticality import Criticality
from .namepatterns import SuiteNamePatterns, TestNamePatterns
from .visitor import SuiteVisitor, SkipAllVisitor
from .totalstatistics import TotalStatisticsBuilder
from .statistics import Statistics
from .itemlist import ItemList
