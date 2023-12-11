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

from typing import Generic, TypeVar, TYPE_CHECKING

from robot.utils import NormalizedDict

from .keywordimplementation import KeywordImplementation

if TYPE_CHECKING:
    from .testlibraries import TestLibrary
    from .resourcemodel import ResourceFile


K = TypeVar('K', bound=KeywordImplementation)


class KeywordFinder(Generic[K]):

    def __init__(self, owner: 'TestLibrary|ResourceFile'):
        self.owner = owner
        self.cache: KeywordCache|None = None

    def find(self, name: str) -> 'list[K]':
        if self.cache is None:
            self.cache = KeywordCache[K](self.owner.keywords)
        return self.cache.find(name)

    def invalidate_cache(self):
        self.cache = None


class KeywordCache(Generic[K]):

    def __init__(self, keywords: 'list[K]'):
        self.normal = NormalizedDict[K](ignore='_')
        self.embedded: list[K] = []
        add_normal = self.normal.__setitem__
        add_embedded = self.embedded.append
        for kw in keywords:
            if kw.embedded:
                add_embedded(kw)
            else:
                add_normal(kw.name, kw)

    def find(self, name: str) -> 'list[K]':
        try:
            return [self.normal[name]]
        except KeyError:
            return [kw for kw in self.embedded if kw.matches(name)]
