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

"""Module implementing test data parsing.

Public API is exposed via the :mod:`robot.api.parsing` module. See its documentation
for more information and examples. If external code needs to import something from
this module directly, issue should be submitted about exposing it explicitly via
:mod:`robot.api.parsing`.
"""

from .lexer import get_tokens, get_resource_tokens, get_init_tokens, Token
from .model import ModelTransformer, ModelVisitor
from .parser import get_model, get_resource_model, get_init_model
from .suitestructure import SuiteStructureBuilder, SuiteStructureVisitor
