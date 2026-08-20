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

import sys
from types import UnionType
from typing import get_args, get_origin, TypeAliasType, TypeVar, Union

if sys.version_info >= (3, 13):
    from typing import NoDefault
else:
    NoDefault = None


class RecursiveAlias:

    def __init__(self, alias):
        self.name = alias.__name__ if isinstance(alias, TypeAliasType) else None
        self.value = None


def resolve_type_alias(alias, context=None):
    if context is None:
        context = {}
    if alias in context:
        return context[alias]
    # RecursiveAlias is used if an alias is used in its own value.
    context[alias] = RecursiveAlias(alias)
    origin = get_origin(alias)
    if origin:
        value = _resolve_generic(origin, get_args(alias), context)
    else:
        value = _resolve(alias, context)
    # Add the resolved value to RecursiveAlias that may be used in the value itself.
    context[alias].value = value
    # Set value in context to the resolved value.
    context[alias] = value
    return value


def _resolve(alias, context):
    value = _get_value(alias)
    origin = get_origin(value)
    if origin:
        origin = Union if origin is UnionType else origin
        args = [resolve_type_alias(a, context) for a in get_args(value)]
        return origin[*args]
    return value


def _get_value(alias):
    seen = set()
    while isinstance(alias, TypeAliasType):
        try:
            value = alias.__value__
            if value in seen:
                raise ValueError("Invalid recursion.")
        except Exception as err:
            raise ValueError(f"Resolving type alias '{alias}' failed: {err}") from None
        else:
            alias = value
            seen.add(value)
    return alias


def _resolve_generic(alias, args, context):
    value = resolve_type_alias(alias, context)
    origin = get_origin(value)
    if origin:
        type_vars = _get_type_var_mapping(value.__parameters__, args)
        args = [_resolve_type_var(arg, type_vars) for arg in get_args(value)]
        return _resolve_generic(origin, args, context)
    if isinstance(alias, TypeAliasType):
        type_vars = _get_type_var_mapping(alias.__parameters__, args)
        return _resolve_type_var(value, type_vars)
    args = [resolve_type_alias(a, context) for a in args]
    return value[*args]


def _get_type_var_mapping(type_vars, values):
    mapping = dict(zip(type_vars, values))
    if len(type_vars) > len(values) and NoDefault is not None:
        for var in type_vars:
            if var not in mapping and var.__default__ is not NoDefault:
                mapping[var] = var.__default__
    return mapping


def _resolve_type_var(arg, type_vars):
    if isinstance(arg, TypeVar):
        try:
            return type_vars[arg]
        except KeyError:
            raise ValueError(f"Type variable '{arg.__name__}' has not value.")
    origin = get_origin(arg)
    if origin:
        args = [_resolve_type_var(a, type_vars) for a in get_args(arg)]
        return origin[*args]
    return arg
