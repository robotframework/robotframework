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

"""Implements test data parsing.

Main entry points to parsing are the following:

* :func:`~.lexer.get_tokens` and :func:`~.lexer.get_resource_tokens`
  for parsing test data to tokens.

* :func:`~.builders.get_model` and :func:`~.builders.get_resource_model` for
  parsing test data into a model represented as an abstract syntax tree (AST).

*TODO:* Document how to modify the returned model using
:class:`~.model.ModelVisitor` and :class:`~.model.ModelTransformer`.
Also mention that the model as well as tokens are part of the public API.

Like with rest of the public API, these functions and classes are exposed
also via :module:`robot.api`.

The :module:`robot.parsing` package has been totally rewritten in Robot
Framework 3.2 and all code using it needs to be updated. Depending on the
use case, it may be possible to use the :func:`robot.running.TestSuiteBuilder`
that has not changed instead.

Example
-------

::

    TODO
"""

from .builders import get_model, get_resource_model
from .lexer import get_tokens, get_resource_tokens, Token
from .model import ModelTransformer, ModelVisitor
from .suitestructure import SuiteStructureBuilder, SuiteStructureVisitor
