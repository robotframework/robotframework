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

from enum import Enum
from inspect import isclass

from robot.running import TypeConverter
from robot.utils import getdoc, Sortable, type_name, typeddict_types

from .standardtypes import STANDARD_TYPE_DOCS

EnumType = type(Enum)


class TypeDoc(Sortable):
    ENUM = "Enum"
    TYPED_DICT = "TypedDict"
    CUSTOM = "Custom"
    STANDARD = "Standard"

    def __init__(
        self,
        type,
        name,
        doc,
        accepts=(),
        usages=None,
        members=None,
        items=None,
    ):
        self.type = type
        self.name = name
        self.doc = doc or ""  # doc parsed from XML can be None.
        self.accepts = [type_name(t) if not isinstance(t, str) else t for t in accepts]
        self.usages = usages or []
        # Enum members and TypedDict items are used only with appropriate types.
        self.members = members
        self.items = items

    @property
    def _sort_key(self):
        return self.name.lower()

    @classmethod
    def for_type(cls, type_info, converters):
        if isinstance(type_info.type, EnumType):
            return cls.for_enum(type_info.type)
        if isinstance(type_info.type, typeddict_types):
            return cls.for_typed_dict(type_info.type)
        converter = TypeConverter.converter_for(type_info, converters)
        if not converter:
            return None
        if not converter.type:
            return cls(
                cls.CUSTOM,
                converter.type_name,
                converter.doc,
                converter.value_types,
            )
        # Get `type_name` from class, not from instance, to get the original
        # name with generics like `list[int]` that override it in instance.
        return cls(
            cls.STANDARD,
            type(converter).type_name,
            STANDARD_TYPE_DOCS[converter.type],
            converter.value_types,
        )

    @classmethod
    def for_enum(cls, enum):
        accepts = (str, int) if issubclass(enum, int) else (str,)
        return cls(
            cls.ENUM,
            enum.__name__,
            getdoc(enum),
            accepts,
            members=[
                EnumMember(name, str(member.value))
                for name, member in enum.__members__.items()
            ],
        )

    @classmethod
    def for_typed_dict(cls, typed_dict):
        items = []
        required_keys = list(getattr(typed_dict, "__required_keys__", []))
        optional_keys = list(getattr(typed_dict, "__optional_keys__", []))
        for key, value in typed_dict.__annotations__.items():
            typ = value.__name__ if isclass(value) else str(value)
            required = key in required_keys if required_keys or optional_keys else None
            items.append(TypedDictItem(key, typ, required))
        return cls(
            cls.TYPED_DICT,
            typed_dict.__name__,
            getdoc(typed_dict),
            accepts=(str, "Mapping"),
            items=items,
        )

    def to_dictionary(self):
        data = {
            "type": self.type,
            "name": self.name,
            "doc": self.doc,
            "usages": self.usages,
            "accepts": self.accepts,
        }
        if self.members is not None:
            data["members"] = [m.to_dictionary() for m in self.members]
        if self.items is not None:
            data["items"] = [i.to_dictionary() for i in self.items]
        return data


class TypedDictItem:

    def __init__(self, key, type, required=None):
        self.key = key
        self.type = type
        self.required = required

    def to_dictionary(self):
        return {"key": self.key, "type": self.type, "required": self.required}


class EnumMember:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def to_dictionary(self):
        return {"name": self.name, "value": self.value}
