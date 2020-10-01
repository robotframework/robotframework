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

from robot.utils import getshortdoc, get_timestamp, Sortable, setter, unic
from robot.libdocpkg.htmlwriter import DocFormatter

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

    def to_dictionary(self):
        return {
            'name': self.name,
            'doc': self.doc,
            'version': self.version,
            'type': self.type,
            'scope': self.scope,
            'named_args': self.named_args,
            'doc_format': self.doc_format,
            'source': self.source,
            'lineno': self.lineno,
            'inits': [init.to_dictionary() for init in self.inits],
            'keywords': [kw.to_dictionary() for kw in self.keywords],
            'generated': get_timestamp(daysep='-', millissep=None),
            'all_tags': tuple(sorted(self.all_tags)),
            'contains_tags': bool(self.all_tags)
            # ToDo: delete that ugly thing when "mikko the slow" fixed the front end
        }

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
        return set(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)

    def convert_doc_to_html(self):
        formatter = DocFormatter(self.keywords, self.doc, self.doc_format)
        self._doc = formatter.html(self.doc, intro=True)
        self.doc_format = 'HTML'
        for init in self.inits:
            init.doc = formatter.html(init.doc)
        for keyword in self.keywords:
            keyword.doc = formatter.html(keyword.doc)


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', tags=(), source=None,
                 lineno=-1):
        self.name = name
        self.args = args
        self.shortdoc = None
        self.doc = doc
        self.tags = tuple(tags)
        self.source = source
        self.lineno = lineno

    def to_dictionary(self):
        return {
            'name': self.name,
            'args': [arg.to_dictionary() for arg in self.args],
            'doc': self.doc,
            'shortdoc': self.shortdoc,
            'tags': self.tags,
            'source': self.source,
            'lineno': self.lineno,
            'matched': True
        }

    @setter
    def doc(self, doc):
        if not self.shortdoc:
            self.shortdoc = ' '.join(getshortdoc(doc).splitlines())
        return doc

    @property
    def deprecated(self):
        return self.doc.startswith('*DEPRECATED') and '*' in self.doc[1:]

    @property
    def _sort_key(self):
        return self.name.lower()


ARG_TYPES = {'POSITIONAL_ONLY': '',
             'POSITIONAL_OR_KEYWORD': '',
             'VAR_POSITIONAL': '*',
             'KEYWORD_ONLY': '',
             'VAR_KEYWORD': '**'}


class ArgumentDoc(object):

    def __init__(self,
                 name='',
                 type=None,
                 default=None,
                 kind='POSITIONAL_OR_KEYWORD',
                 required=True):
        self.name = name
        self._type = type
        self.default = default
        self.kind = kind
        self.required = required

    def to_dictionary(self):
        return {
            'name': self.name,
            'type': self.type,
            'default': self.default.value if self.default else None,
            'kind': self.kind,
            'required': self.required,
            'string_repr': str(self)
        }

    @property
    def type(self):
        if self._type is None:
            return
        if isclass(self._type):
            return self._type.__name__
        type_name = str(self._type)
        if type_name.startswith('typing.'):
            type_name = type_name[len('typing.'):]
        return type_name

    def __str__(self):
        kw_string = ARG_TYPES[self.kind] + self.name
        kw_string += self._format_type()
        kw_string += self._format_enum_values()
        kw_string += self._format_default()
        return kw_string

    def _format_type(self):
        if not self.type:
            return ''
        return ': {}'.format(self.type)

    def _format_enum_values(self):
        if isclass(self._type) and issubclass(self._type, Enum):
            return ' {{ {} }}'.format(self._format_enum(self._type))
        return ''

    @staticmethod
    def _format_enum(enum):
        try:
            members = list(enum.__members__)
        except AttributeError:  # old enum module
            members = [attr for attr in dir(enum) if not attr.startswith('_')]
        while len(members) > 3 and len(' | '.join(members)) > 42:
            members[-2:] = ['...']
        return ' | '.join(members)

    def _format_default(self):
        if self.kind in ['VAR_POSITIONAL',
                         'VAR_KEYWORD'] or self.required:
            return ''
        default_str = ' = ' if self.type else '='
        default_str += str(self.default)
        return default_str


class DefaultValue(object):

    def __init__(self, value=None):
        self.value = value

    @setter
    def value(self, value):
        if value is None:
            return 'None'
        if isinstance(value, str):
            return self._escape_defaults_str(value)
        if isinstance(value, Enum):
            return value.name
        return unic(value)

    def __str__(self):
        return str(self.value)

    @staticmethod
    def _escape_defaults_str(value):
        if value == '':
            return '${Empty}'
        value_repr = repr(value)[1:-1]
        return re.sub('^(?= )|(?<= )$|(?<= )(?= )', r'\\', value_repr)
