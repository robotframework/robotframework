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
from enum import Enum

from robot.utils import Sortable, typeddict_types
from robot.running import TypeConverter


EnumType = type(Enum)


class DataTypeCatalog:

    def __init__(self, converters=None):
        self._converters = converters
        self._customs = set()
        self._enums = set()
        self._typed_dicts = set()

    def __iter__(self):
        return iter(sorted(self._customs | self._enums | self._typed_dicts))

    def __bool__(self):
        return next(iter(self), None) is not None

    @property
    def customs(self):
        return sorted(self._customs)

    @property
    def enums(self):
        return sorted(self._enums)

    @property
    def typed_dicts(self):
        return sorted(self._typed_dicts)

    def update(self, types):
        storages = {CustomDoc: self._customs,
                    EnumDoc: self._enums,
                    TypedDictDoc: self._typed_dicts}
        for typ in types:
            type_doc = self._get_type_doc_object(typ)
            for type_cls in storages:
                if isinstance(type_doc, type_cls):
                    storages[type_cls].add(type_doc)

    def _get_type_doc_object(self, typ):
        if isinstance(typ, DataType):
            return typ
        if isinstance(typ, EnumType):
            return EnumDoc.from_type(typ)
        if isinstance(typ, typeddict_types):
            return TypedDictDoc.from_type(typ)
        info = TypeConverter.type_info_for(typ, self._converters)
        if info:
            return CustomDoc(info.name, info.doc)
        if isinstance(typ, dict) and 'type' in typ:
            cls = {EnumDoc.type: EnumDoc,
                   TypedDictDoc.type: TypedDictDoc,
                   CustomDoc.type: CustomDoc}.get(typ['type'])
            if cls:
                typ.pop('type')
                return cls(**typ)
        return None

    def to_dictionary(self):
        return {
            'customs': [t.to_dictionary() for t in self.customs],
            'enums': [t.to_dictionary() for t in self.enums],
            'typedDicts': [t.to_dictionary() for t in self.typed_dicts]
        }


class DataType(Sortable):
    type = None

    def __init__(self, name, doc):
        self.name = name
        self.doc = doc

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
        }


class TypedDictDoc(DataType):
    type = 'TypedDict'

    def __init__(self, name, doc, items=None):
        super().__init__(name, doc)
        self.items = items or []

    @classmethod
    def from_type(cls, typed_dict):
        items = []
        required_keys = list(getattr(typed_dict, '__required_keys__', []))
        optional_keys = list(getattr(typed_dict, '__optional_keys__', []))
        for key, value in typed_dict.__annotations__.items():
            typ = value.__name__ if isclass(value) else str(value)
            required = key in required_keys if required_keys or optional_keys else None
            items.append({'key': key, 'type': typ, 'required': required})
        return cls(name=typed_dict.__name__,
                   doc=getdoc(typed_dict) or '',
                   items=items)

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
            'items': self.items
        }


class EnumDoc(DataType):
    type = 'Enum'

    def __init__(self, name, doc, members=None):
        super().__init__(name, doc)
        self.members = members or []

    @classmethod
    def from_type(cls, enum_type):
        return cls(name=enum_type.__name__,
                   doc=getdoc(enum_type) or '',
                   members=[{'name': name, 'value': str(member.value)}
                            for name, member in enum_type.__members__.items()])

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
            'members': self.members
        }


class CustomDoc(DataType):
    type = 'Custom'
