#  Copyright 2008-2014 Nokia Solutions and Networks
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

"""Package with reusable and extendable model classes.

This package contains base classes, for example, for
:class:`test suites <robot.model.testsuite.TestSuite>`,
:class:`test cases <robot.model.testcase.TestCase>` and
:class:`keywords <robot.model.keyword.Keyword>`, and for other generic
functionality, such as :mod:`visitors <robot.model.visitor>`.

These classes are extended both in :mod:`robot.result` and :mod:`robot.running`
packages and used also elsewhere. There should, however, be no need to
externally use these classes directly, and they are not part of the public API.

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
