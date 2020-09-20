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
from inspect import isclass
from itertools import chain
import re

from robot.model import Tags
from robot.utils import getshortdoc, Sortable, setter, unic

from .writer import LibdocWriter
from .output import LibdocOutput

try:
    from enum import Enum
except ImportError:  # Standard in Py 3.4+ but can be separately installed
    class Enum(object):
        pass


class LibraryDoc(object):

    def __init__(self, name='', doc='', version='', type='LIBRARY',
                 scope='TEST', named_args=True, doc_format='ROBOT',
                 source=None, lineno=-1):
        self.name = name
        self._doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.named_args = named_args
        self.doc_format = doc_format
        self.source = source
        self.lineno = lineno
        self.inits = []
        self.keywords = []

    @property
    def doc(self):
        if self.doc_format == 'ROBOT' and '%TOC%' in self._doc:
            return self._add_toc(self._doc)
        return self._doc

    def _add_toc(self, doc):
        toc = self._create_toc(doc)
        return '\n'.join(line if line.strip() != '%TOC%' else toc
                         for line in doc.splitlines())

    def _create_toc(self, doc):
        entries = re.findall(r'^\s*=\s+(.+?)\s+=\s*$', doc, flags=re.MULTILINE)
        if self.inits:
            entries.append('Importing')
        entries.append('Keywords')
        return '\n'.join('- `%s`' % entry for entry in entries)

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def keywords(self, kws):
        return sorted(kws)

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', tags=(), source=None,
                 lineno=-1):
        self.name = name
        self.args = args
        self.doc = doc
        self.tags = Tags(tags)
        self.source = source
        self.lineno = lineno

    @property
    def shortdoc(self):
        return getshortdoc(self.doc)

    @property
    def deprecated(self):
        return self.doc.startswith('*DEPRECATED') and '*' in self.doc[1:]

    @property
    def _sort_key(self):
        return self.name.lower()


ARG_TYPES = {'positional': '',
             'varargs': '*',
             'kwonlyargs': '',
             'kwargs': '**'}


class ArgumentDoc(object):

    def __init__(self,
                 name='',
                 value_type=None,
                 default_value=None,
                 argument_type='positional',
                 optional=False):
        self.name = name
        self.value_type = value_type
        self.default_value = default_value
        self.argument_type = self._validate_arg_type(argument_type)
        self.optional = optional

    def __str__(self):
        kw_string = ARG_TYPES[self.argument_type] + self.name
        kw_string += self._format_type()
        kw_string += self._format_enum_values()
        kw_string += self._format_default()
        return kw_string

    def _format_type(self):
        if not self.value_type:
            return ''
        if isclass(self.value_type):
            return ': {}'.format(self.value_type.__name__)
        return ': {}'.format(self.value_type)

    def _format_default(self):
        if self.argument_type in ['varargs', 'kwargs'] or not self.optional:
            return ''
        default_str = ' = ' if self.value_type else '='
        default_str += unic(self.default_value)
        return default_str

    def _format_enum_values(self):
        if isclass(self.value_type) and issubclass(self.value_type, Enum):
            return ' {{ {} }}'.format(self._format_enum(self.value_type))
        return ''

    @staticmethod
    def _validate_arg_type(arg_type):
        if arg_type.lower() not in ARG_TYPES:
            raise ValueError("Invalid argument_type '{}'."
                             "Valid values are {}.".
                             format(arg_type, ", ".join(ARG_TYPES.keys()))
                             )
        return arg_type.lower()

    @staticmethod
    def _format_enum(enum):
        try:
            members = list(enum.__members__)
        except AttributeError:  # old enum module
            members = [attr for attr in dir(enum) if not attr.startswith('_')]
        while len(members) > 3 and len(' | '.join(members)) > 42:
            members[-2:] = ['...']
        return ' | '.join(members)
