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
from robot.utils import plural_or_not, seq2str
from robot.variables import is_list_variable


class ArgumentValidator(object):

    def __init__(self, argspec):
        """:type argspec: :py:class:`robot.running.arguments.ArgumentSpec`"""
        self._argspec = argspec

    def validate(self, positional, named, dryrun=False):
        if dryrun and any(is_list_variable(arg) for arg in positional):
            return
        named = set(name for name, value in named)
        self._validate_no_multiple_values(positional, named, self._argspec)
        self._validate_positional_limits(positional, named, self._argspec)
        self._validate_no_mandatory_missing(positional, named, self._argspec)
        self._validate_no_named_only_missing(named, self._argspec)
        self._validate_no_extra_named(named, self._argspec)

    def _validate_positional_limits(self, positional, named, spec):
        count = len(positional) + self._named_positionals(named, spec)
        if not spec.minargs <= count <= spec.maxargs:
            self._raise_wrong_count(count, spec)

    def _named_positionals(self, named, spec):
        if not spec.supports_named:
            return 0
        return sum(1 for n in named if n in spec.positional)

    def _raise_wrong_count(self, count, spec):
        minend = plural_or_not(spec.minargs)
        if spec.minargs == spec.maxargs:
            expected = '%d argument%s' % (spec.minargs, minend)
        elif not spec.varargs:
            expected = '%d to %d arguments' % (spec.minargs, spec.maxargs)
        else:
            expected = 'at least %d argument%s' % (spec.minargs, minend)
        if spec.kwargs or spec.kwonlyargs:
            expected = expected.replace('argument', 'non-named argument')
        raise DataError("%s '%s' expected %s, got %d."
                        % (spec.type, spec.name, expected, count))

    def _validate_no_multiple_values(self, positional, named, spec):
        if named and spec.supports_named:
            for name in spec.positional[:len(positional)]:
                if name in named:
                    raise DataError("%s '%s' got multiple values for argument "
                                    "'%s'." % (spec.type, spec.name, name))

    def _validate_no_mandatory_missing(self, positional, named, spec):
        for name in spec.positional[len(positional):spec.minargs]:
            if name not in named:
                raise DataError("%s '%s' missing value for argument '%s'."
                                % (spec.type, spec.name, name))

    def _validate_no_named_only_missing(self, named, spec):
        defined = set(named) | set(spec.defaults)
        missing = [arg for arg in spec.kwonlyargs if arg not in defined]
        if missing:
            raise DataError("%s '%s' missing named-only argument%s %s."
                            % (spec.type, spec.name, plural_or_not(missing),
                               seq2str(sorted(missing))))

    def _validate_no_extra_named(self, named, spec):
        if not spec.kwargs:
            extra = set(named) - set(spec.positional) - set(spec.kwonlyargs)
            if extra:
                raise DataError("%s '%s' got unexpected named argument%s %s."
                                % (spec.type, spec.name, plural_or_not(extra),
                                   seq2str(sorted(extra))))
