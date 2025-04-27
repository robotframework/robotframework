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

from .body import (
    BaseBody as BaseBody,
    BaseBranches as BaseBranches,
    BaseIterations as BaseIterations,
    Body as Body,
    BodyItem as BodyItem,
)
from .configurer import SuiteConfigurer as SuiteConfigurer
from .control import (
    Break as Break,
    Continue as Continue,
    Error as Error,
    For as For,
    ForIteration as ForIteration,
    Group as Group,
    If as If,
    IfBranch as IfBranch,
    Return as Return,
    Try as Try,
    TryBranch as TryBranch,
    Var as Var,
    While as While,
    WhileIteration as WhileIteration,
)
from .fixture import create_fixture as create_fixture
from .itemlist import ItemList as ItemList
from .keyword import Keyword as Keyword
from .message import Message as Message, MessageLevel as MessageLevel
from .modelobject import DataDict as DataDict, ModelObject as ModelObject
from .modifier import ModelModifier as ModelModifier
from .statistics import Statistics as Statistics
from .tags import TagPattern as TagPattern, TagPatterns as TagPatterns, Tags as Tags
from .testcase import TestCase as TestCase, TestCases as TestCases
from .testsuite import TestSuite as TestSuite, TestSuites as TestSuites
from .totalstatistics import (
    TotalStatistics as TotalStatistics,
    TotalStatisticsBuilder as TotalStatisticsBuilder,
)
from .visitor import SuiteVisitor as SuiteVisitor
