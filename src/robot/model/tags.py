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

from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, overload, Sequence

from robot.utils import normalize, NormalizedDict, Matcher


class Tags(Sequence[str]):
    __slots__ = ['_tags', '_reserved']

    def __init__(self, tags: Iterable[str] = ()):
        if isinstance(tags, Tags):
            self._tags, self._reserved = tags._tags, tags._reserved
        else:
            self._tags, self._reserved = self._init_tags(tags)

    def robot(self, name: str) -> bool:
        """Check do tags contain a reserved tag in format `robot:<name>`.

        This is same as `'robot:<name>' in tags` but considerably faster.
        """
        return name in self._reserved

    def _init_tags(self, tags) -> 'tuple[tuple[str, ...], tuple[str, ...]]':
        if not tags:
            return (), ()
        if isinstance(tags, str):
            tags = (tags,)
        return self._normalize(tags)

    def _normalize(self, tags):
        nd = NormalizedDict([(str(t), None) for t in tags], ignore='_')
        if '' in nd:
            del nd['']
        if 'NONE' in nd:
            del nd['NONE']
        reserved = tuple(tag[6:] for tag in nd.normalized_keys if tag[:6] == 'robot:')
        return tuple(nd), reserved

    def add(self, tags: Iterable[str]):
        self.__init__(tuple(self) + tuple(Tags(tags)))

    def remove(self, tags: Iterable[str]):
        match = TagPatterns(tags).match
        self.__init__([t for t in self if not match(t)])

    def match(self, tags: Iterable[str]) -> bool:
        return TagPatterns(tags).match(self)

    def __contains__(self, tags: Iterable[str]) -> bool:
        return self.match(tags)

    def __len__(self) -> int:
        return len(self._tags)

    def __iter__(self) -> Iterator[str]:
        return iter(self._tags)

    def __str__(self) -> str:
        tags = ', '.join(self)
        return f'[{tags}]'

    def __repr__(self) -> str:
        return repr(list(self))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Iterable):
            return False
        if not isinstance(other, Tags):
            other = Tags(other)
        self_normalized = [normalize(tag, ignore='_') for tag in self]
        other_normalized = [normalize(tag, ignore='_') for tag in other]
        return sorted(self_normalized) == sorted(other_normalized)

    @overload
    def __getitem__(self, index: int) -> str:
        ...

    @overload
    def __getitem__(self, index: slice) -> 'Tags':
        ...

    def __getitem__(self, index: 'int|slice') -> 'str|Tags':
        if isinstance(index, slice):
            return Tags(self._tags[index])
        return self._tags[index]

    def __add__(self, other: Iterable[str]) -> 'Tags':
        return Tags(tuple(self) + tuple(Tags(other)))


class TagPatterns(Sequence['TagPattern']):

    def __init__(self, patterns: Iterable[str]):
        self._patterns = tuple(TagPattern.from_string(p) for p in Tags(patterns))

    def match(self, tags: Iterable[str]) -> bool:
        if not self._patterns:
            return False
        tags = normalize_tags(tags)
        return any(p.match(tags) for p in self._patterns)

    def __contains__(self, tag: str) -> bool:
        return self.match(tag)

    def __len__(self) -> int:
        return len(self._patterns)

    def __iter__(self) -> Iterator['TagPattern']:
        return iter(self._patterns)

    def __getitem__(self, index: int) -> 'TagPattern':
        return self._patterns[index]

    def __str__(self) -> str:
        patterns = ', '.join(str(pattern) for pattern in self)
        return f'[{patterns}]'


class TagPattern(ABC):

    @classmethod
    def from_string(cls, pattern: str) -> 'TagPattern':
        pattern = pattern.replace(' ', '')
        if 'NOT' in pattern:
            must_match, *must_not_match = pattern.split('NOT')
            return NotTagPattern(must_match, must_not_match)
        if 'OR' in pattern:
            return OrTagPattern(pattern.split('OR'))
        if 'AND' in pattern or '&' in pattern:
            return AndTagPattern(pattern.replace('&', 'AND').split('AND'))
        return SingleTagPattern(pattern)

    @abstractmethod
    def match(self, tags: Iterable[str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator['TagPattern']:
        raise NotImplementedError

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class SingleTagPattern(TagPattern):

    def __init__(self, pattern: str):
        # Normalization is handled here, not in Matcher, for performance reasons.
        # This way we can normalize tags only once.
        self._matcher = Matcher(normalize(pattern, ignore='_'),
                                caseless=False, spaceless=False)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return self._matcher.match_any(tags)

    def __iter__(self) -> Iterator['TagPattern']:
        yield self

    def __str__(self) -> str:
        return self._matcher.pattern

    def __bool__(self) -> bool:
        return bool(self._matcher)


class AndTagPattern(TagPattern):

    def __init__(self, patterns: Iterable[str]):
        self._patterns = tuple(TagPattern.from_string(p) for p in patterns)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return all(p.match(tags) for p in self._patterns)

    def __iter__(self) -> Iterator['TagPattern']:
        return iter(self._patterns)

    def __str__(self) -> str:
        return ' AND '.join(str(pattern) for pattern in self)


class OrTagPattern(TagPattern):

    def __init__(self, patterns: Iterable[str]):
        self._patterns = tuple(TagPattern.from_string(p) for p in patterns)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return any(p.match(tags) for p in self._patterns)

    def __iter__(self) -> Iterator['TagPattern']:
        return iter(self._patterns)

    def __str__(self) -> str:
        return ' OR '.join(str(pattern) for pattern in self)


class NotTagPattern(TagPattern):

    def __init__(self, must_match: str, must_not_match: Iterable[str]):
        self._first = TagPattern.from_string(must_match)
        self._rest = OrTagPattern(must_not_match)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return ((self._first.match(tags) or not self._first)
                and not self._rest.match(tags))

    def __iter__(self) -> Iterator['TagPattern']:
        yield self._first
        yield from self._rest

    def __str__(self) -> str:
        return ' NOT '.join(str(pattern) for pattern in self).lstrip()


def normalize_tags(tags: Iterable[str]) -> Iterable[str]:
    """Performance optimization to normalize tags only once."""
    if isinstance(tags, NormalizedTags):
        return tags
    if isinstance(tags, str):
        tags = [tags]
    return NormalizedTags([normalize(t, ignore='_') for t in tags])


class NormalizedTags(list):
    pass
