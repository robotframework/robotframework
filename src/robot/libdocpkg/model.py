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
from collections import OrderedDict
from inspect import isclass
from itertools import chain
import json
import re
try:
    from enum import Enum
    EnumType = type(Enum)
except ImportError:  # Standard in Py 3.4+ but can be separately installed
    class EnumType(object):
        pass

try:
    from typing import TypedDict
    TypedDictType = type(TypedDict('TypedDictDummy', {}))
except ImportError:
    class TypedDictType(object):
        pass

try:
    from typing_extensions import TypedDict as ExtTypedDict
    ExtTypedDictType = type(ExtTypedDict('TypedDictDummy', {}))
except ImportError:
    class ExtTypedDictType(object):
        pass

from robot.model import Tags
from robot.utils import (IRONPYTHON, getshortdoc, get_timestamp,
                         Sortable, setter, type_name, unicode, unic)

from .htmlutils import HtmlToText, DocFormatter
from .writer import LibdocWriter
from .output import LibdocOutput


class LibraryDoc(object):

    def __init__(self, name='', doc='', version='', type='LIBRARY',
                 scope='TEST', doc_format='ROBOT',
                 source=None, lineno=-1):
        self.name = name
        self._doc = doc
        self.version = version
        self.type = type
        self.scope = scope
        self.doc_format = doc_format
        self.source = source
        self.lineno = lineno
        self.data_types_catalog = {}
        self.inits = []
        self.keywords = []

    @property
    def data_types(self):
        return self.data_types_catalog.values()

    @data_types.setter
    def data_types(self, data_types):
        list_of_type_docs = [self._get_type_doc_object(_type) for _type in data_types]
        self.data_types_catalog = dict([(t.name, t) for t in list_of_type_docs])

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
        if self.keywords:
            entries.append('Keywords')
        if self.data_types_catalog:
            entries.append('Data types')
        return '\n'.join('- `%s`' % entry for entry in entries)

    @setter
    def doc_format(self, format):
        return format or 'ROBOT'

    @setter
    def inits(self, inits):
        return self._sort_keywords(inits)

    @setter
    def keywords(self, kws):
        return self._sort_keywords(kws)

    def _sort_keywords(self, kws):
        for keyword in kws:
            self._add_types_from_keyword(keyword)
            keyword.parent = self
            keyword.generate_shortdoc()
        return sorted(kws)

    def _add_types_from_keyword(self, keyword):
        for arg in keyword.args:
            for type_repr, typ in zip(arg.types_reprs, arg.types):
                if type_repr not in self.data_types_catalog:
                    type_doc = self._get_type_doc_object(typ)
                    if type_doc:
                        self.data_types_catalog[type_repr] = type_doc

    def _get_type_doc_object(self, typ):
        if isinstance(typ, (EnumDoc, TypedDictDoc)):
            return typ
        if isinstance(typ, (TypedDictType, ExtTypedDictType)):
            return TypedDictDoc.from_TypedDict(typ)
        if isinstance(typ, EnumType):
            return EnumDoc.from_Enum(typ)
        if isinstance(typ, dict):
            if typ.get('super', None) == 'TypedDict':
                return TypedDictDoc.from_dict(typ)
            if typ.get('super', None) == 'Enum':
                return EnumDoc.from_dict(typ)
        return None

    @property
    def all_tags(self):
        return Tags(chain.from_iterable(kw.tags for kw in self.keywords))

    def save(self, output=None, format='HTML'):
        with LibdocOutput(output, format) as outfile:
            LibdocWriter(format).write(self, outfile)

    def convert_docs_to_html(self):
        formatter = DocFormatter(self.keywords, self.data_types, self.doc, self.doc_format)
        self._doc = formatter.html(self.doc, intro=True)
        self.doc_format = 'HTML'
        for init in self.inits:
            init.doc = formatter.html(init.doc)
        for keyword in self.keywords:
            keyword.doc = formatter.html(keyword.doc)
        for type_doc in self.data_types_catalog.values():
            type_doc.doc = formatter.html(type_doc.doc)

    def to_dictionary(self):
        return {
            'name': self.name,
            'doc': self.doc,
            'version': self.version,
            'generated': get_timestamp(daysep='-', millissep=None),
            'type': self.type,
            'scope': self.scope,
            'docFormat': self.doc_format,
            'source': self.source,
            'lineno': self.lineno,
            'tags': list(self.all_tags),
            'inits': [init.to_dictionary() for init in self.inits],
            'keywords': [kw.to_dictionary() for kw in self.keywords],
            'dataTypes': [dt.to_dictionary() for dt in
                          sorted(self.data_types, key=lambda t: t.name)]
        }

    def to_json(self, indent=None):
        data = self.to_dictionary()
        if IRONPYTHON:
            # Workaround for https://github.com/IronLanguages/ironpython2/issues/643
            data = self._unicode_to_utf8(data)
        return json.dumps(data, indent=indent)

    def _unicode_to_utf8(self, data):
        if isinstance(data, dict):
            return {self._unicode_to_utf8(key): self._unicode_to_utf8(value)
                    for key, value in data.items()}
        if isinstance(data, (list, tuple)):
            return [self._unicode_to_utf8(item) for item in data]
        if isinstance(data, unicode):
            return data.encode('UTF-8')
        return data


class KeywordDoc(Sortable):

    def __init__(self, name='', args=(), doc='', shortdoc='', tags=(), source=None,
                 lineno=-1, parent=None):
        self.name = name
        self.args = args
        self.doc = doc
        self._shortdoc = shortdoc
        self.tags = Tags(tags)
        self.source = source
        self.lineno = lineno
        self.parent = parent

    @property
    def shortdoc(self):
        if self._shortdoc:
            return self._shortdoc
        return self._get_shortdoc()

    def _get_shortdoc(self):
        doc = self.doc
        if self.parent and self.parent.doc_format == 'HTML':
            doc = HtmlToText().get_shortdoc_from_html(doc)
        return ' '.join(getshortdoc(doc).splitlines())

    @shortdoc.setter
    def shortdoc(self, shortdoc):
        self._shortdoc = shortdoc

    @property
    def deprecated(self):
        return self.doc.startswith('*DEPRECATED') and '*' in self.doc[1:]

    @property
    def _sort_key(self):
        return self.name.lower()

    def generate_shortdoc(self):
        if not self._shortdoc:
            self.shortdoc = self._get_shortdoc()

    def to_dictionary(self):
        return {
            'name': self.name,
            'args': [self._arg_to_dict(arg) for arg in self.args],
            'doc': self.doc,
            'shortdoc': self.shortdoc,
            'tags': list(self.tags),
            'source': self.source,
            'lineno': self.lineno
        }

    def _arg_to_dict(self, arg):
        return {
            'name': arg.name,
            'types': arg.types_reprs,
            'default': arg.default_repr,
            'kind': arg.kind,
            'required': arg.required,
            'repr': unicode(arg)
        }


class TypedDictDoc(object):

    def __init__(self, name='', super='', doc='', items=None,
                 required_keys=None, optional_keys=None):
        self.name = name
        self.super = super
        self.doc = doc
        self.items = items or {}
        self.required_keys = required_keys or []
        self.optional_keys = optional_keys or []

    @classmethod
    def from_dict(cls, type_doc):
        if isinstance(type_doc, dict):
            return cls(name=type_doc['name'],
                       super=type_doc['super'],
                       doc=type_doc['doc'],
                       items=type_doc['items'],
                       required_keys=type_doc['required_keys'],
                       optional_keys=type_doc['optional_keys'])
        raise TypeError(
            'TypedDictDoc.from_dict() requires dictionary types but got %s.'
            % type_name(type_doc))

    @classmethod
    def from_TypedDict(cls, typed_dict):
        if isinstance(typed_dict, (TypedDictType, ExtTypedDictType)):
            items = {}
            for key, value in typed_dict.__annotations__.items():
                items[key] = value.__name__ if isclass(value) else unic(value)
            return cls(name=typed_dict.__name__,
                       super='TypedDict',
                       doc=typed_dict.__doc__ if typed_dict.__doc__ else '',
                       items=items,
                       required_keys=list(getattr(typed_dict, '__required_keys__', [])),
                       optional_keys=list(getattr(typed_dict, '__optional_keys__', [])))
        raise TypeError(
            'TypedDictDoc.from_TypedDict() requires a TypedDict but got %s.'
            % type_name(typed_dict))

    def to_dictionary(self):
        return {
            'name': self.name,
            'super': self.super,
            'doc': self.doc,
            'items': self.items,
            'required_keys': self.required_keys,
            'optional_keys': self.optional_keys
        }


class EnumDoc(object):

    def __init__(self, name='', super='', doc='', members=None):
        self.name = name
        self.super = super
        self.doc = doc
        self.members = members or []

    @classmethod
    def from_dict(cls, type_doc):
        if isinstance(type_doc, dict):
            return cls(name=type_doc['name'],
                       super=type_doc['super'],
                       doc=type_doc['doc'],
                       members=type_doc['members'])
        raise TypeError(
            'EnumDoc.from_dict() requires dictionary types but got %s.'
            % type_name(type_doc))

    @classmethod
    def from_Enum(cls, enum_type):
        if isinstance(enum_type, EnumType):
            return cls(name=enum_type.__name__,
                       super='Enum',
                       doc=enum_type.__doc__ or '',
                       members=[{'name': name, 'value': unicode(member.value)}
                                for name, member in enum_type.__members__.items()])
        raise TypeError(
            'EnumDoc.from_Enum() requires Enum types but got %s.'
            % type_name(enum_type))

    def to_dictionary(self):
        return {
            'name': self.name,
            'super': self.super,
            'doc': self.doc,
            'members': self.members
        }
