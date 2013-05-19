#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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


class ArgumentMapper(object):

    def __init__(self, argspec):
        self._argspec = argspec

    def map(self, positional, named, variables=None, fill_all_defaults=True):
        template = KeywordCallTemplate(self._argspec, variables)
        template.fill_positional(positional)
        template.fill_named(named)
        if not fill_all_defaults:
            template.prune_last_defaults()
        template.fill_defaults()
        return list(template)


class KeywordCallTemplate(object):

    def __init__(self, argspec, variables):
        defaults = argspec.defaults
        if variables:
            defaults = variables.replace_list(defaults)
        self._template = [None] * argspec.minargs + [Default(value) for value in defaults]
        self._positional = argspec.positional

    def fill_positional(self, positional):
        self._template[:len(positional)] = positional

    def fill_named(self, named):
        for name, value in named.items():
            index = self._positional.index(name)
            self._template[index] = value

    def prune_last_defaults(self):
        for index, val in reversed(list(enumerate(self._template))):
            if not isinstance(val, Default):
                return
            self._template.pop(index)

    def fill_defaults(self):
        for index, val in enumerate(self._template):
            if isinstance(val, Default):
                self._template[index] = val.value

    def __iter__(self):
        return iter(self._template)


class Default(object):

    def __init__(self, value):
        self.value=value