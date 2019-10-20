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

from ast import literal_eval
from collections import OrderedDict
try:
    from collections import abc
except ImportError:    # Python 2
    import collections as abc
from datetime import datetime, date, timedelta
from decimal import InvalidOperation, Decimal
try:
    from enum import Enum
except ImportError:    # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass
from numbers import Integral, Real

from robot.libraries.DateTime import convert_date, convert_time
from robot.utils import unicode

import importlib

from robot.running.context import EXECUTION_CONTEXTS
from .typeconverters import TypeConverter

import re


class TypingResolver(object):

    def _get_converter_type(self, type_):
        if isinstance(type_, (str, unicode)) :
            if type_ in ('None', 'NoneType'):
                return 'NoneType'
            type_result =  TypeConverter._type_aliases.get(type_.lower(), None)
            if type_result:
                return type_result
            type_result = globals().get(type_, None)
            if type_result:
                return type_result
            type_result = getattr(abc, type_, None)
            if type_result:
                return type_result
            class_data = type_.rsplit(".")
            if len(class_data) > 1:
                module_path = ".".join(class_data[:-1])
                class_str = class_data[-1]
                try:
                    context = EXECUTION_CONTEXTS.current
                    if context:
                        type_result = getattr(context.namespace._kw_store.libraries[module_path].get_instance(), class_str)
                except Exception as e:
                    pass
                if type_result:
                    return type_result
        return None

    def _get_class_from_nonetype(self, type_):
        if type_ in ('None', 'NoneType'):
            return type(None)
        return None

    def _get_class_from_normal_type(self, type_):
        try:
            type_ = eval(type_)
        except Exception as e:
            type_ = None
        return type_

    def _get_class_from_iterable_type(self, type_):
        return globals().get(type_, None)

    def _get_class_from_abc_module(self, type_):
        return getattr(abc, type_, None)

    def _get_class_from_imported_module(self, type_):
        class_data = type_.rsplit(".")
        type_result = None
        if len(class_data) > 1:
            module_path = ".".join(class_data[:-1])
            class_str = class_data[-1]
            try:
                context = EXECUTION_CONTEXTS.current
                if context:
                    type_result = getattr(context.namespace._kw_store.libraries[module_path].get_instance(), class_str)
            except Exception as e:
                pass
        return type_result

    def _get_str_from_alias(self, type_):
        return type_.lower()

    def _get_class_by_type_name(self, type_):
        return self._get_class_from_nonetype(type_) or \
        self._get_class_from_normal_type(type_) or \
        self._get_class_from_iterable_type(type_) or \
        self._get_class_from_abc_module(type_) or \
        self._get_class_from_imported_module(type_) or \
        self._get_str_from_alias(type_)

    def _get_class_by_typing_module(self, type_):
        from typing import (List, Sequence, MutableSequence,
                    Dict, Mapping, MutableMapping,
                    Set, MutableSet)
        return locals().get(type_, None)

    def _parse_typing_format(self, type_):
        square_bracket_index = type_.index('[')
        typing_name = type_[0:square_bracket_index]
        type_in_bracket = type_[square_bracket_index:]
        return typing_name, [t.strip() for t in type_in_bracket[1:-1].split(',')]

    def _get_typing_class(self, type_):
        main_type, list_of_typing_type = self._parse_typing_format(type_)
        main_type = self._get_class_by_typing_module(main_type)
        main_type.__args__ = (t for t in list_of_typing_type)
        return main_type

    def get_class_of_type(self, type_):
        if isinstance(type_, (str, unicode)) :
            if '[' in type_:
                return self._get_typing_class(type_)
            return self._get_class_by_type_name(type_)
        return None

    def _get_type_in_string_format(self, type_):
        type_ = type_[1:].strip()
        if type_.startswith("'") and type_.endswith("'"):
            type_ = type_[1:-1]
        return type_

    def split_args_and_types(self, arg):
        pattern = re.compile('^[$@&]{[a-zA-Z0-9 ]+(:[^}]*)?}')
        match = pattern.match(arg)
        type_ = None
        if match:
            type_ = match.group(1)
        if type_:
            arg = arg.replace(type_, '', 1)
            type_ = self._get_type_in_string_format(type_)
        return arg, self.get_class_of_type(type_)
