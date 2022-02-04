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


class TypeDoc(Sortable):
    type = None

    def __init__(self, name, doc):
        self.name = name
        self.doc = doc

    @classmethod
    def for_type(cls, type, converters):
        if isinstance(type, EnumType):
            return EnumDoc.from_type(type)
        if isinstance(type, typeddict_types):
            return TypedDictDoc.from_type(type)
        info = TypeConverter.type_info_for(type, converters)
        if info:
            return CustomDoc(info.name, info.doc)
        return None

    @property
    def _sort_key(self):
        return self.name.lower()

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
        }


class TypedDictDoc(TypeDoc):
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
            items.append(TypedDictItem(key, typ, required))
        return cls(name=typed_dict.__name__,
                   doc=getdoc(typed_dict) or '',
                   items=items)

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
            'items': [i.to_dictionary() for i in self.items]
        }


class TypedDictItem:

    def __init__(self, key, type, required=None):
        self.key = key
        self.type = type
        self.required = required

    def to_dictionary(self):
        return {'key': self.key,
                'type': self.type,
                'required': self.required}


class EnumDoc(TypeDoc):
    type = 'Enum'

    def __init__(self, name, doc, members=None):
        super().__init__(name, doc)
        self.members = members or []

    @classmethod
    def from_type(cls, enum_type):
        return cls(name=enum_type.__name__,
                   doc=getdoc(enum_type) or '',
                   members=[EnumMember(name, str(member.value))
                            for name, member in enum_type.__members__.items()])

    def to_dictionary(self):
        return {
            'type': self.type,
            'name': self.name,
            'doc': self.doc,
            'members': [m.to_dictionary() for m in self.members]
        }


class EnumMember:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dictionary(self):
        return {
            'name': self.name,
            'value': self.value
        }


class CustomDoc(TypeDoc):
    type = 'Custom'
