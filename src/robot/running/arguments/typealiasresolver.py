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


def resolve_type_alias(alias):
    origin = get_origin(alias)
    if origin:
        return resolve_generic_type_alias(origin, get_args(alias))
    value = alias
    while isinstance(value, TypeAliasType):
        try:
            value = value.__value__
        except Exception as err:
            raise ValueError(f"Resolving type alias '{value}' failed: {err}")
    origin = get_origin(value)
    if origin:
        origin = Union if origin is UnionType else origin
        args = [resolve_type_alias(a) for a in get_args(value)]
        return origin[*args]
    return value


def resolve_generic_type_alias(alias, args):
    value = resolve_type_alias(alias)
    origin = get_origin(value)
    if origin:
        type_vars = _get_type_var_mapping(value.__parameters__, args)
        args = [_resolve_type_var(arg, type_vars) for arg in get_args(value)]
        return resolve_generic_type_alias(origin, args)
    if isinstance(alias, TypeAliasType):
        type_vars = _get_type_var_mapping(alias.__parameters__, args)
        return _resolve_type_var(value, type_vars)
    args = [resolve_type_alias(a) for a in args]
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
