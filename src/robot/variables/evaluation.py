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

import builtins
import token
from collections.abc import Mapping
from io import StringIO
from tokenize import generate_tokens, untokenize

from robot.errors import DataError
from robot.utils import get_error_message, type_name

from .notfound import variable_not_found


PYTHON_BUILTINS = set(builtins.__dict__)


def evaluate_expression(expression, variable_store, modules=None, namespace=None):
    try:
        if not isinstance(expression, str):
            raise TypeError(f'Expression must be string, got {type_name(expression)}.')
        if not expression:
            raise ValueError('Expression cannot be empty.')
        return _evaluate(expression, variable_store, modules, namespace)
    except Exception:
        raise DataError(f"Evaluating expression '{expression}' failed: "
                        f"{get_error_message()}")


def _evaluate(expression, variable_store, modules=None, namespace=None):
    if '$' in expression:
        expression = _decorate_variables(expression, variable_store)
    # Given namespace must be included in our custom local namespace to make
    # it possible to detect which names are not found and should be imported
    # automatically as modules. It must be also be used as the global namespace
    # with `eval()` because lambdas and possibly other special constructs don't
    # see the local namespace at all.
    namespace = dict(namespace) if namespace else {}
    if modules:
        namespace.update(_import_modules(modules))
    local_ns = EvaluationNamespace(variable_store, namespace)
    return eval(expression, namespace, local_ns)


def _decorate_variables(expression, variable_store):
    variable_started = False
    variable_found = False
    tokens = []
    for toknum, tokval, _, _, _ in generate_tokens(StringIO(expression).readline):
        if variable_started:
            if toknum == token.NAME:
                if tokval not in variable_store:
                    variable_not_found('$%s' % tokval,
                                       variable_store.as_dict(decoration=False),
                                       deco_braces=False)
                tokval = 'RF_VAR_' + tokval
                variable_found = True
            else:
                tokens.append((token.ERRORTOKEN, '$'))
            variable_started = False
        if toknum == token.ERRORTOKEN and tokval == '$':
            variable_started = True
        else:
            tokens.append((toknum, tokval))
    return untokenize(tokens).strip() if variable_found else expression


def _import_modules(module_names):
    modules = {}
    for name in module_names.replace(' ', '').split(','):
        if not name:
            continue
        modules[name] = __import__(name)
        # If we just import module 'root.sub', module 'root' is not found.
        while '.' in name:
            name, _ = name.rsplit('.', 1)
            modules[name] = __import__(name)
    return modules


class EvaluationNamespace(Mapping):

    def __init__(self, variable_store, namespace):
        self.namespace = namespace
        self.variables = variable_store

    def __getitem__(self, key):
        if key.startswith('RF_VAR_'):
            return self.variables[key[7:]]
        if key in self.namespace:
            return self.namespace[key]
        return self._import_module(key)

    def _import_module(self, name):
        if name in PYTHON_BUILTINS:
            raise KeyError
        try:
            return __import__(name)
        except ImportError:
            raise NameError(f"name '{name}' is not defined nor importable as module")

    def __iter__(self):
        yield from self.variables
        yield from self.namespace

    def __len__(self):
        return len(self.variables) + len(self.namespace)
