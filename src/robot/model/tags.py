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
from typing import Iterable, Iterator, overload, Sequence

from robot.utils import Matcher, normalize, NormalizedDict


class Tags(Sequence[str]):
    __slots__ = ("_tags", "_reserved")

    def __init__(self, tags: Iterable[str] = ()):
        if isinstance(tags, Tags):
            self._tags, self._reserved = tags._tags, tags._reserved
        else:
            self._tags, self._reserved = self._init_tags(tags)

    def robot(self, name: str) -> bool:
        """Check do tags contain a reserved tag in format `robot:<name>`.

        `tags.robot('<name>')` is same as `'robot:<name>' in tags`, but using
        this method is considerably faster. This method requires the ``name``
        to be in lowercase, though, while checking with `in` is case-insensitive.
        """
        return name in self._reserved

    def _init_tags(self, tags) -> "tuple[tuple[str, ...], tuple[str, ...]]":
        if not tags:
            return (), ()
        if isinstance(tags, str):
            tags = (tags,)
        return self._normalize(tags)

    def _normalize(self, tags):
        nd = NormalizedDict.fromkeys([str(t) for t in tags], ignore="_")
        # Inspecting already normalized names is performance optimization.
        normalized = nd.normalized_keys
        if "" in normalized:
            del nd[""]
        if "none" in normalized:
            del nd["none"]
        reserved = [n[6:] for n in normalized if n[:6] == "robot:"]
        return tuple(nd), tuple(reserved)

    def add(self, tags: Iterable[str], remove_negated: bool = False):
        tags = Tags(tags)
        if remove_negated:
            remove = [t[1:] for t in tags if t[0] == "-"]
            if remove:
                self._remove(remove, "removing tags using '-tag' syntax")
                tags = [t for t in tags if t[0] != "-"]
        self.__init__([*self, *tags])

    def remove(self, tags: Iterable[str]):
        self._remove(tags, "removing tags")

    def _remove(self, tags: Iterable[str], usage):
        match = TagPatterns(tags, usage).match
        self.__init__([t for t in self if not match(t)])

    def match(self, tags: Iterable[str]) -> bool:
        return TagPatterns(tags, "matching tags").match(self)

    def __contains__(self, tags: Iterable[str]) -> bool:
        return self.match(tags)

    def __len__(self) -> int:
        return len(self._tags)

    def __iter__(self) -> Iterator[str]:
        return iter(self._tags)

    def __str__(self) -> str:
        tags = ", ".join(self)
        return f"[{tags}]"

    def __repr__(self) -> str:
        return repr(list(self))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Iterable):
            return False
        if not isinstance(other, Tags):
            other = Tags(other)
        self_normalized = [normalize(tag, ignore="_") for tag in self]
        other_normalized = [normalize(tag, ignore="_") for tag in other]
        return sorted(self_normalized) == sorted(other_normalized)

    @overload
    def __getitem__(self, index: int) -> str: ...

    @overload
    def __getitem__(self, index: slice) -> "Tags": ...

    def __getitem__(self, index: "int|slice") -> "str|Tags":
        if isinstance(index, slice):
            return Tags(self._tags[index])
        return self._tags[index]

    def __add__(self, other: Iterable[str]) -> "Tags":
        return Tags([*self, *Tags(other)])


class TagPatterns(Sequence["TagPattern"]):
    """Represents a list of tag patterns like ``tag``, ``t*`` or ``x OR y``.

    The ``usage`` parameter should only be used internally by Robot Framework
    itself. See ``TagPattern.from_string`` for more details if needed.
    """

    def __init__(self, patterns: Iterable[str] = (), usage: "str | None" = None):
        self._patterns = tuple(TagPattern.from_string(p, usage) for p in Tags(patterns))

    @property
    def is_constant(self):
        return all(p.is_constant for p in self._patterns)

    def match(self, tags: Iterable[str]) -> bool:
        if not self._patterns:
            return False
        tags = normalize_tags(tags)
        return any(p.match(tags) for p in self._patterns)

    def __contains__(self, tag: str) -> bool:
        return self.match(tag)

    def __len__(self) -> int:
        return len(self._patterns)

    def __iter__(self) -> Iterator["TagPattern"]:
        return iter(self._patterns)

    def __getitem__(self, index: int) -> "TagPattern":
        return self._patterns[index]

    def __str__(self) -> str:
        patterns = ", ".join(str(pattern) for pattern in self)
        return f"[{patterns}]"


class TagPattern(ABC):
    is_constant = False

    @classmethod
    def from_string(cls, pattern: str, usage: "str | None" = None) -> "TagPattern":
        """Create ``TagPattern`` object from string like ``tag``, ``t*`` or ``x OR y``.

        ``usage`` is used in a deprecation warning if a pattern uses Boolean operators
        in deprecated format like ``XORY``. It should only be used internally by
        Robot Framework itself for giving context where the pattern was used. When
        a usage is given, warning is logged using Robot's own global ``LOGGER`` and
        otherwise the warning is logged using Python's ``logging`` module.
        """
        if "NOT" in pattern:
            must_match, *must_not_match = cls._split(pattern, "NOT", usage)
            return NotTagPattern(must_match, must_not_match)
        if "OR" in pattern:
            return OrTagPattern(cls._split(pattern, "OR", usage))
        if "&" in pattern:
            cls._deprecated(
                pattern,
                "Boolean operator '&' is deprecated, use 'AND' instead.",
                usage,
            )
            pattern = pattern.replace("&", " AND ")
        if "AND" in pattern:
            return AndTagPattern(cls._split(pattern, "AND", usage))
        return SingleTagPattern(pattern)

    @classmethod
    def _split(cls, pattern, operator, usage=None):
        tokens = f" {pattern} ".split(operator)
        for token in tokens:
            if not cls._validate(token, operator):
                cls._deprecated(
                    pattern,
                    f"'{operator}' is currently considered to be a Boolean operator, "
                    f"but in the future operators must be surrounded with spaces or "
                    f"tag names must be lower case.",
                    usage,
                )
                break
        return tokens

    @classmethod
    def _validate(cls, token, operator):
        if not token or token[0].isspace() and token[-1].isspace():
            return True
        remaining_operators = {"NOT": ("OR", "AND"), "OR": ("AND",), "AND": ()}
        for exclude in remaining_operators[operator]:
            if exclude in token:
                token = token.replace(exclude, "")
        return token.lower() == token

    @classmethod
    def _deprecated(cls, pattern, message, usage=None):
        message = (
            f"The behavior of tag pattern '{pattern}' will change in "
            f"Robot Framework 8.0: {message}"
        )
        if usage:
            from robot.output import LOGGER

            LOGGER.warn(f"Problems when {usage}: {message}")
        else:
            import warnings

            warnings.warn(message)

    @abstractmethod
    def match(self, tags: Iterable[str]) -> bool:
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterator["TagPattern"]:
        raise NotImplementedError

    def __getitem__(self, index: int) -> "TagPattern":
        return list(self)[index]

    @abstractmethod
    def __str__(self) -> str:
        raise NotImplementedError


class SingleTagPattern(TagPattern):

    def __init__(self, pattern: str):
        # Normalization is handled here, not in Matcher, for performance reasons.
        # With this configuration all normalizations in Matcher are no-ops.
        self._matcher = Matcher(
            normalize(pattern, ignore="_"),
            caseless=False,
            spaceless=False,
        )
        # Preserve original patter mostly for string representation purposes.
        self._pattern = pattern.strip()

    @property
    def is_constant(self):
        pattern = self._pattern
        return not ("*" in pattern or "?" in pattern or "[" in pattern)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return self._matcher.match_any(tags)

    def __iter__(self) -> Iterator["TagPattern"]:
        yield self

    def __str__(self) -> str:
        return self._pattern

    def __bool__(self) -> bool:
        return bool(self._matcher)


class AndTagPattern(TagPattern):

    def __init__(self, patterns: Iterable[str]):
        self._patterns = tuple(TagPattern.from_string(p) for p in patterns)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return all(p.match(tags) for p in self._patterns)

    def __iter__(self) -> Iterator["TagPattern"]:
        return iter(self._patterns)

    def __str__(self) -> str:
        return " AND ".join(str(pattern) for pattern in self)


class OrTagPattern(TagPattern):

    def __init__(self, patterns: Iterable[str]):
        self._patterns = tuple(TagPattern.from_string(p) for p in patterns)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        return any(p.match(tags) for p in self._patterns)

    def __iter__(self) -> Iterator["TagPattern"]:
        return iter(self._patterns)

    def __str__(self) -> str:
        return " OR ".join(str(pattern) for pattern in self)


class NotTagPattern(TagPattern):

    def __init__(self, must_match: str, must_not_match: Iterable[str]):
        self._first = TagPattern.from_string(must_match)
        self._rest = OrTagPattern(must_not_match)

    def match(self, tags: Iterable[str]) -> bool:
        tags = normalize_tags(tags)
        if self._first and not self._first.match(tags):
            return False
        return not self._rest.match(tags)

    def __iter__(self) -> Iterator["TagPattern"]:
        yield self._first
        yield from self._rest

    def __str__(self) -> str:
        return " NOT ".join(str(pattern) for pattern in self).lstrip()


def normalize_tags(tags: Iterable[str]) -> Iterable[str]:
    """Performance optimization to normalize tags only once."""
    if isinstance(tags, NormalizedTags):
        return tags
    if isinstance(tags, str):
        tags = [tags]
    return NormalizedTags([normalize(t, ignore="_") for t in tags])


class NormalizedTags(list):
    pass
