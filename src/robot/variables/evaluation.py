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

from tokenize import generate_tokens, untokenize
import token

from robot.errors import DataError
from robot.utils import (get_error_message, is_string, NormalizedDict,
                         StringIO, type_name)

from .notfound import variable_not_found
from .tablesetter import VariableTableValueBase


def evaluate_expression(expression, variable_store=None, modules=None,
                        namespace=None):
    try:
        if not is_string(expression):
            raise TypeError("Expression must be string, got %s."
                            % type_name(expression))
        if not expression:
            raise ValueError("Expression cannot be empty.")
        return _evaluate(expression, variable_store, modules, namespace)
    except:
        raise DataError("Evaluating expression '%s' failed: %s"
                        % (expression, get_error_message()))


def _evaluate(expression, variable_store=None, modules=None, namespace=None):
    if '$' in expression and variable_store:
        expression, variables = \
            _handle_variables_in_expression(expression, variable_store)
    else:
        variables = {}
    namespace = _create_evaluation_namespace(namespace, modules)
    return eval(expression, namespace, variables)


def _handle_variables_in_expression(expression, variable_store):
    variables = None
    variable_started = False
    tokens = []
    for toknum, tokval, _, _, _ in generate_tokens(StringIO(expression).readline):
        if variable_started:
            if toknum == token.NAME:
                if variables is None:
                    variables = variable_store.as_dict(decoration=False)
                if tokval not in variables:
                    variable_not_found('$%s' % tokval, variables,
                                       deco_braces=False)
                tokval = 'RF_VAR_' + tokval
            else:
                tokens.append((token.ERRORTOKEN, '$'))
            variable_started = False
        if toknum == token.ERRORTOKEN and tokval == '$':
            variable_started = True
        else:
            tokens.append((toknum, tokval))
    if variables is None:
        return expression, {}
    expression = untokenize(tokens).strip()
    variables = VariableNamespace(variables, variable_store)
    return expression, variables


def _create_evaluation_namespace(namespace, modules):
    namespace = dict(namespace or {})
    modules = modules.replace(' ', '').split(',') if modules else []
    namespace.update((m, __import__(m)) for m in modules if m)
    return namespace


class VariableNamespace(NormalizedDict):

    def __init__(self, variables, variable_store):
        decorated = [('RF_VAR_' + name, variables[name]) for name in variables]
        NormalizedDict.__init__(self, decorated, ignore='_')
        self._variable_store = variable_store

    def __getitem__(self, key):
        value = NormalizedDict.__getitem__(self, key)
        if isinstance(value, VariableTableValueBase):
            item = (key[len('RF_VAR_'):], value)
            value = self._variable_store.resolve_delayed(item)
            self[key] = value
        return value
