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

from typing import TYPE_CHECKING

from robot.errors import DataError
from robot.utils import (is_dict_like, is_list_like, plural_or_not as s,
                         seq2str, type_name)

if TYPE_CHECKING:
    from .argumentspec import ArgumentSpec


class TypeValidator:

    def __init__(self, arg_spec: 'ArgumentSpec'):
        self.arg_spec = arg_spec

    def validate(self, types):
        if types is None:
            return None
        if not types:
            return {}
        if is_dict_like(types):
            return self.validate_type_dict(types)
        if is_list_like(types):
            return self.convert_type_list_to_dict(types)
        raise DataError(f'Type information must be given as a dictionary or '
                        f'a list, got {type_name(types)}.')

    def validate_type_dict(self, types):
        # 'return' isn't used for anything yet, but it may be shown by Libdoc
        # in the future. Trying to be forward compatible.
        names = set(self.arg_spec.argument_names + ['return'])
        extra = [t for t in types if t not in names]
        if extra:
            raise DataError(f'Type information given to non-existing '
                            f'argument{s(extra)} {seq2str(sorted(extra))}.')
        return types

    def convert_type_list_to_dict(self, types):
        names = self.arg_spec.argument_names
        if len(types) > len(names):
            raise DataError(f'Type information given to {len(types)} argument{s(types)} '
                            f'but keyword has only {len(names)} argument{s(names)}.')
        return {name: value for name, value in zip(names, types) if value}
