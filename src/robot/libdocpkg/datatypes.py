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

from inspect import getdoc, isclass

try:
    from enum import Enum

    EnumType = type(Enum)
except ImportError:  # Standard in Py 3.4+ but can be separately installed
    class EnumType(object):
        pass


from robot.utils import py3to2, Sortable, unic, unicode, typeddict_types


@py3to2
class DataTypeCatalog(object):

    def __init__(self):
        self._enums = set()
        self._typed_dicts = set()

    def __iter__(self):
        return iter(sorted(self._typed_dicts | self._enums))

    def __bool__(self):
        return bool(self._enums or self._typed_dicts)

    @property
    def enums(self):
        return sorted(self._enums)

    @property
    def typed_dicts(self):
        return sorted(self._typed_dicts)

    def update(self, types):
        for typ in types:
            type_doc = self._get_type_doc_object(typ)
            if isinstance(type_doc, EnumDoc):
                self._enums.add(type_doc)
            elif isinstance(type_doc, TypedDictDoc):
                self._typed_dicts.add(type_doc)

    def _get_type_doc_object(self, typ):
        if isinstance(typ, (EnumDoc, TypedDictDoc)):
            return typ
        if isinstance(typ, typeddict_types):
            return TypedDictDoc.from_TypedDict(typ)
        if isinstance(typ, EnumType):
            return EnumDoc.from_Enum(typ)
        if isinstance(typ, dict):
            if typ.get('type', None) == 'TypedDict':
                return TypedDictDoc(**typ)
            if typ.get('type', None) == 'Enum':
                return EnumDoc(**typ)
        return None

    def to_dictionary(self):
        return {
            'enums': [en.to_dictionary() for en in self.enums],
            'typedDicts': [td.to_dictionary() for td in self.typed_dicts]
        }


class TypedDictDoc(Sortable):

    def __init__(self, name='', doc='', items=None, type='TypedDict'):
        self.name = name
        self.doc = doc
        self.items = items or []
        self.type = type

    @classmethod
    def from_TypedDict(cls, typed_dict):
        items = []
        required_keys = list(getattr(typed_dict, '__required_keys__', []))
        optional_keys = list(getattr(typed_dict, '__optional_keys__', []))
        for key, value in typed_dict.__annotations__.items():
            typ = value.__name__ if isclass(value) else unic(value)
            required = key in required_keys if required_keys or optional_keys else None
            items.append({'key': key, 'type': typ, 'required': required})
        return cls(name=typed_dict.__name__,
                   doc=getdoc(typed_dict) or '',
                   items=items)

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        return {
            'name': self.name,
            'type': self.type,
            'doc': self.doc,
            'items': self.items
        }


class EnumDoc(Sortable):

    def __init__(self, name='', doc='', members=None, type='Enum'):
        self.name = name
        self.doc = doc
        self.members = members or []
        self.type = type

    @classmethod
    def from_Enum(cls, enum_type):
        return cls(name=enum_type.__name__,
                   doc=getdoc(enum_type) or '',
                   members=[{'name': name, 'value': unicode(member.value)}
                            for name, member in enum_type.__members__.items()])

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        return {
            'name': self.name,
            'type': self.type,
            'doc': self.doc,
            'members': self.members
        }
