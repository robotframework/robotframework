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

"""Package with generic, reusable and extensible model classes.

This package contains, for example, :class:`~robot.model.testsuite.TestSuite`,
:class:`~robot.model.testcase.TestCase`, :class:`~robot.model.keyword.Keyword`
and :class:`~robot.model.visitor.SuiteVisitor` base classes.
These classes are extended both by :mod:`execution <robot.running.model>`
and :mod:`result <robot.result.model>` related model objects and used also
elsewhere.

This package is considered stable.
"""

from .body import BaseBody, Body, BodyItem, Branches
from .configurer import SuiteConfigurer
from .control import For, While, If, IfBranch, Try, TryBranch, Return, Continue, Break
from .testsuite import TestSuite
from .testcase import TestCase
from .keyword import Keyword, Keywords
from .message import Message, Messages
from .modifier import ModelModifier
from .tags import Tags, TagPattern, TagPatterns
from .namepatterns import SuiteNamePatterns, TestNamePatterns
from .visitor import SuiteVisitor
from .totalstatistics import TotalStatisticsBuilder
from .statistics import Statistics
from .itemlist import ItemList
