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

"""This package contains base classes e.g. for
:py:class:`suites <robot.model.testsuite.TestSuite>`,
:py:class:`test cases <robot.model.testcase.TestCase>`,
:py:class:`keywords <robot.model.keyword.Keyword>` and for other generic
functionality, such as :py:mod:`visitors <robot.model.visitor>`.

These base classes are inherited both in packages :py:mod:`robot.result` and
:py:mod:`robot.running`. For example,
:py:class:`robot.model.testsuite.TestSuite` is extended in
:py:mod:`running <robot.running>` by
:py:class:`robot.running.model.TestSuite`
and :py:class:`robot.model.visitor` in :py:mod:`result <robot.result>`
by :py:class:`robot.result.visitor.ResultVisitor`.

The modules in this package are used internally by Robot Framework
and are not intended to be used as public APIs.

This package is considered stable.
"""

from .configurer import SuiteConfigurer
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
from .imports import Imports
from .itemlist import ItemList
