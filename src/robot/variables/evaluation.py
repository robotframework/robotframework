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
from robot.utils import (get_error_message, is_string, MutableMapping, PY2,
                         StringIO, type_name)

from .notfound import variable_not_found


if PY2:
    import __builtin__ as builtins
else:
    import builtins
PYTHON_BUILTINS = set(builtins.__dict__)


def evaluate_expression(expression, variable_store, modules=None,
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


def _evaluate(expression, variable_store, modules=None, namespace=None):
    if '$' in expression:
        expression = _decorate_variables(expression, variable_store)
    global_ns = _import_modules(modules) if modules else {}
    local_ns = EvaluationNamespace(variable_store, namespace)
    return eval(expression, global_ns, local_ns)


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


# TODO: In Python 3 this could probably be just Mapping, not MutableMapping.
# With Python 2 at least list comprehensions need to mutate the evaluation
# namespace. Using just Mapping would allow removing __set/delitem__.
class EvaluationNamespace(MutableMapping):

    def __init__(self, variable_store, namespace=None):
        self.namespace = {} if namespace is None else dict(namespace)
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
            raise NameError("name '%s' is not defined nor importable as module"
                            % name)

    def __setitem__(self, key, value):
        if key.startswith('RF_VAR_'):
            self.variables[key[7:]] = value
        else:
            self.namespace[key] = value

    def __delitem__(self, key):
        if key.startswith('RF_VAR_'):
            del self.variables[key[7:]]
        else:
            del self.namespace[key]

    def __iter__(self):
        for key in self.variables:
            yield key
        for key in self.namespace:
            yield key

    def __len__(self):
        return len(self.variables) + len(self.namespace)
