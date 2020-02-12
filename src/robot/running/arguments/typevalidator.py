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

from robot.errors import DataError
from robot.utils import (is_dict_like, is_list_like, plural_or_not as s,
                         seq2str, type_name)


class TypeValidator(object):

    def __init__(self, argspec):
        """:type argspec: :py:class:`robot.running.arguments.ArgumentSpec`"""
        self._argspec = argspec

    def validate(self, types):
        if types is None:
            return None
        if not types:
            return {}
        if is_dict_like(types):
            return self.validate_type_dict(types)
        if is_list_like(types):
            return self.convert_type_list_to_dict(types)
        raise DataError('Type information must be given as a dictionary or '
                        'a list, got %s.' % type_name(types))

    def validate_type_dict(self, types):
        # 'return' isn't used for anything yet but it may be shown by Libdoc
        # in the future. Trying to be forward compatible.
        names = set(self._argspec.argument_names + ['return'])
        extra = [t for t in types if t not in names]
        if extra:
            raise DataError('Type information given to non-existing '
                            'argument%s %s.'
                            % (s(extra), seq2str(sorted(extra))))
        return types

    def convert_type_list_to_dict(self, types):
        names = self._argspec.argument_names
        if len(types) > len(names):
            raise DataError('Type information given to %d argument%s but '
                            'keyword has only %d argument%s.'
                            % (len(types), s(types), len(names), s(names)))
        return {name: value for name, value in zip(names, types) if value}
