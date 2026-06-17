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
import textwrap
from collections.abc import Generator
from dataclasses import dataclass, field


# TODO: Add slots=True when RF drops Python 3.8 support — @dataclass(slots=True)
#       requires 3.10+ and eliminates per-instance __dict__ overhead, which matters
#       at 100k+ keyword scale.
@dataclass
class ParsedDocString:
    doc: str
    args: "dict[str, str]" = field(default_factory=dict)
    returns: str = ""


# Headers are matched case-insensitively — 'args:' and 'Args:' are equivalent.
_ARGS_HEADERS = frozenset({"args:", "arguments:", "parameters:"})
# Minimum indent to recognise an arg entry (2 supports both 2-space and 4-space
# indented arg lists). Maximum is 4 (standard Google style).
_MIN_ARG_INDENT = 2
_MAX_ARG_INDENT = 4
_RETURNS_HEADERS = frozenset({"returns:", "yields:"})


def parse_docstring(doc: str) -> ParsedDocString:
    """Always returns a ParsedDocString — never raises."""
    try:
        return _parse(doc)
    except (TypeError, AttributeError):
        return ParsedDocString(doc="", args={}, returns="")


def _parse(doc: str) -> ParsedDocString:
    lines = doc.splitlines()
    doc_parts = []
    args: dict[str, str] = {}
    returns = ""
    for header, body in _iter_sections(lines):
        if header is None:
            doc_parts.append("\n".join(body))
        elif header.lower() in _ARGS_HEADERS:
            args = _parse_args(body)
        elif header.lower() in _RETURNS_HEADERS:
            returns = _parse_returns(body)
        else:
            # Unrecognised section: reassemble and preserve in doc. The header's
            # trailing whitespace is normalised by rstrip() in _is_section_boundary,
            # and the final doc is rstrip'd, so trailing whitespace is not fully preserved.
            doc_parts.append(header + "\n" + "\n".join(body))
    assembled = "\n".join(doc_parts).lstrip("\n").rstrip()
    # Each prose part ends with the blank lines that separate it from the next
    # section, so joining parts with "\n" naturally produces the correct "\n\n"
    # paragraph separator between them without any special-casing.
    return ParsedDocString(doc=assembled, args=args, returns=returns)


def _iter_sections(
    lines: "list[str]",
) -> "Generator[tuple[str | None, list[str]], None, None]":
    """Yields (header | None, body_lines) pairs — pure grouping, no classification."""
    header, body = None, []
    for line in lines:
        boundary = _is_section_boundary(line)
        if boundary:
            yield header, body
            header, body = boundary, []
        elif header is not None and _ends_section_body(line):
            # A line with indent < 2 inside a section body ends the section
            # and starts a new prose group (e.g. a Robot Framework Tags: line).
            yield header, body
            header, body = None, [line]
        else:
            body.append(line)
    yield header, body


def _is_section_boundary(line: str) -> str:
    if not line or line[0] in (" ", "\t"):
        return ""
    stripped = line.rstrip()
    if stripped.endswith(":"):
        return stripped
    return ""


def _ends_section_body(line: str) -> bool:
    """Return True if a non-empty line has less than 2 spaces of leading indent."""
    if not line:
        return False
    first = line[0]
    if first not in (" ", "\t"):
        return True  # 0 indent
    return len(line) == 1 or line[1] not in (" ", "\t")  # exactly 1 indent char


def _bare_arg_name(raw: str) -> str:
    """Return the bare identifier from a decorated arg name token.

    Strips Python-style asterisks (*args, **kwargs) and RF variable markers
    (${name}, @{varargs}, &{kwargs}), returning just the identifier.
    """
    if len(raw) >= 3 and raw[0] in "$@&" and raw[1] == "{" and raw[-1] == "}":
        return raw[2:-1]
    return raw.lstrip("*")


def _iter_arg_entries(
    lines: "list[str]",
) -> "Generator[tuple[str, str, list[str]], None, None]":
    name = None
    inline_parts: list[str] = []
    raw_body: list[str] = []
    in_block = False

    for line in lines:
        if not line:
            if name is not None:
                if in_block:
                    raw_body.append(line)
                else:
                    # Blank line mid-inline-description: promote to block so the
                    # paragraph break is preserved rather than silently dropped.
                    in_block = True
                    raw_body = []
            continue
        indent = len(line) - len(line.lstrip())
        if _MIN_ARG_INDENT <= indent <= _MAX_ARG_INDENT:
            lstripped = line.lstrip()
            before, sep, after = lstripped.rstrip().partition(":")
            # Google style: colon must be followed by a space or end of line.
            # This rejects URLs ("https://") and key:value pairs.
            if sep and (not after or after[0] == " "):
                raw_name = before.partition("(")[0].rstrip()
                is_rf_var = (
                    len(raw_name) >= 3
                    and raw_name[0] in "$@&"
                    and raw_name[1] == "{"
                    and raw_name[-1] == "}"
                )
                bare = _bare_arg_name(raw_name)
                if is_rf_var and bare.strip() or not is_rf_var and bare.isidentifier():
                    if name is not None:
                        yield name, " ".join(inline_parts), raw_body
                    name = bare
                    first = after.strip()
                    inline_parts = [first] if first else []
                    raw_body = []
                    in_block = not first
                    continue
        if name is not None:
            if in_block:
                raw_body.append(line)
            else:
                inline_parts.append(line.strip())

    if name is not None:
        yield name, " ".join(inline_parts), raw_body


def _build_arg_desc(inline_text: str, raw_body: "list[str]") -> str:
    if not raw_body:
        return inline_text
    block = textwrap.dedent("\n".join(raw_body)).strip()
    if not inline_text:
        return block
    return (inline_text + "\n\n" + block) if block else inline_text


def _parse_args(lines: "list[str]") -> "dict[str, str]":
    return {
        name: _build_arg_desc(inline_text, raw_body)
        for name, inline_text, raw_body in _iter_arg_entries(lines)
    }


def _parse_returns(lines: "list[str]") -> str:
    return textwrap.dedent("\n".join(lines)).strip()
