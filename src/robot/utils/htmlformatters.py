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

import re
from functools import partial
from itertools import cycle


class LinkFormatter:
    _image_exts = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg")
    _link = re.compile(r"\[(.+?\|.*?)]")
    _url = re.compile(
        r"""
        ((^|\ ) ["'(\[{]*)           # begin of line or space and opt. any char "'([{
        ([a-z][\w+-.]*://[^\s|]+?)   # url
        (?=[)\]}"'.,!?:;|]* ($|\ ))  # opt. any char )]}"'.,!?:;| and eol or space
        """,
        re.VERBOSE | re.MULTILINE | re.IGNORECASE,
    )

    def format_url(self, text):
        return self._format_url(text, format_as_image=False)

    def _format_url(self, text, format_as_image=True):
        if "://" not in text:
            return text
        return self._url.sub(partial(self._replace_url, format_as_image), text)

    def _replace_url(self, format_as_image, match):
        pre = match.group(1)
        url = match.group(3)
        if format_as_image and self._is_image(url):
            return pre + self._get_image(url)
        return pre + self._get_link(url)

    def _get_image(self, src, title=None):
        return f'<img src="{self._quot(src)}" title="{self._quot(title or src)}">'

    def _get_link(self, href, content=None):
        return f'<a href="{self._quot(href)}">{content or href}</a>'

    def _quot(self, attr):
        return attr if '"' not in attr else attr.replace('"', "&quot;")

    def format_link(self, text):
        # 2nd, 4th, etc. token contains link, others surrounding content
        tokens = self._link.split(text)
        formatters = cycle((self._format_url, self._format_link))
        return "".join(f(t) for f, t in zip(formatters, tokens))

    def _format_link(self, text):
        link, content = [t.strip() for t in text.split("|", 1)]
        if self._is_image(content):
            content = self._get_image(content, link)
        elif self._is_image(link):
            return self._get_image(link, content)
        return self._get_link(link, content)

    def _is_image(self, text):
        return text.startswith("data:image/") or text.lower().endswith(self._image_exts)


class LineFormatter:
    newline = "\n"
    _bold = re.compile(
        r"""
        (                          # prefix (group 1)
          (^|\ )                   # begin of line or space
          ["'(]* _?                # opt. any char "'( and opt. start of italics
        )                          #
        \*                         # start of bold
        ([^\ ].*?)                 # no space and then anything (group 3)
        \*                         # end of bold
        (?=                        # start of postfix (non-capturing group)
          _? ["').,!?:;]*          # optional end of italic and any char "').,!?:;
          ($|\ )                   # end of line or space
        )
        """,
        re.VERBOSE,
    )
    _italic = re.compile(
        r"""
        ( (^|\ ) ["'(]* )          # begin of line or space and opt. any char "'(
        _                          # start of italics
        ([^\ _].*?)                # no space or underline and then anything
        _                          # end of italics
        (?= ["').,!?:;]* ($|\ ) )  # opt. any char "').,!?:; and end of line or space
        """,
        re.VERBOSE,
    )
    _code = re.compile(
        r"""
        ( (^|\ ) ["'(]* )          # same as above with _ changed to ``
        ``
        ([^\ `].*?)
        ``
        (?= ["').,!?:;]* ($|\ ) )
        """,
        re.VERBOSE,
    )

    def __init__(self):
        self._formatters = [
            ("*", self._format_bold),
            ("_", self._format_italic),
            ("``", self._format_code),
            ("", LinkFormatter().format_link),
        ]

    def handles(self, line):
        return True

    def format(self, line):
        for marker, formatter in self._formatters:
            if marker in line:
                line = formatter(line)
        return line

    def _format_bold(self, line):
        return self._bold.sub("\\1<b>\\3</b>", line)

    def _format_italic(self, line):
        return self._italic.sub("\\1<i>\\3</i>", line)

    def _format_code(self, line):
        return self._code.sub("\\1<code>\\3</code>", line)


class HtmlFormatter:

    def __init__(self):
        self._formatters = [
            TableFormatter(),
            PreformattedFormatter(),
            ListFormatter(),
            HeaderFormatter(),
            RulerFormatter(),
        ]
        self._formatters.append(ParagraphFormatter(self._formatters[:]))
        self._current = None

    def format(self, text):
        results = []
        for line in text.splitlines():
            self._process_line(line, results)
        self._end_current(results)
        return "\n".join(results)

    def _process_line(self, line, results):
        if not line.strip():
            self._end_current(results)
        elif self._current and self._current.handles(line):
            self._current.add(line)
        else:
            self._end_current(results)
            self._current = self._find_formatter(line)
            self._current.add(line)

    def _end_current(self, results):
        if self._current:
            results.append(self._current.end())
            self._current = None

    def _find_formatter(self, line):
        for formatter in self._formatters:
            if formatter.handles(line):
                return formatter


class _Formatter:
    _strip_lines = True

    def __init__(self):
        self._lines = []

    def handles(self, line):
        return self._handles(line.strip() if self._strip_lines else line)

    def _handles(self, line):
        raise NotImplementedError

    def add(self, line):
        self._lines.append(line.strip() if self._strip_lines else line)

    def end(self):
        result = self.format(self._lines)
        self._lines = []
        return result

    def format(self, lines):
        raise NotImplementedError


class _SingleLineFormatter(_Formatter):

    def _handles(self, line):
        return not self._lines and self.match(line)

    def match(self, line):
        raise NotImplementedError

    def format(self, lines):
        return self.format_line(lines[0])

    def format_line(self, line):
        raise NotImplementedError


class RulerFormatter(_SingleLineFormatter):
    match = re.compile("^-{3,}$").match

    def format_line(self, line):
        return "<hr>"


class HeaderFormatter(_SingleLineFormatter):
    match = re.compile(r"^(={1,3})\s+(\S.*?)\s+\1$").match

    def format_line(self, line):
        level, text = self.match(line).groups()
        level = len(level) + 1
        return f"<h{level}>{text}</h{level}>"


class ParagraphFormatter(_Formatter):
    _format_line = LineFormatter().format

    def __init__(self, other_formatters):
        super().__init__()
        self._other_formatters = other_formatters

    def _handles(self, line):
        return not any(other.handles(line) for other in self._other_formatters)

    def format(self, lines):
        return f"<p>{self._format_line(' '.join(lines))}</p>"


class TableFormatter(_Formatter):
    _table_line = re.compile(r"^\| (.* |)\|$")
    _line_splitter = re.compile(r" \|(?= )")
    _format_cell_content = LineFormatter().format

    def _handles(self, line):
        return self._table_line.match(line) is not None

    def format(self, lines):
        return self._format_table([self._split_to_cells(li) for li in lines])

    def _split_to_cells(self, line):
        return [cell.strip() for cell in self._line_splitter.split(line[1:-1])]

    def _format_table(self, rows):
        row_len = max(len(row) for row in rows)
        table = ['<table border="1">']
        for row in rows:
            row += [""] * (row_len - len(row))  # fix ragged tables
            table.append("<tr>")
            table.extend(self._format_cell(cell) for cell in row)
            table.append("</tr>")
        table.append("</table>")
        return "\n".join(table)

    def _format_cell(self, content):
        if content.startswith("=") and content.endswith("="):
            tx = "th"
            content = content[1:-1].strip()
        else:
            tx = "td"
        return f"<{tx}>{self._format_cell_content(content)}</{tx}>"


class PreformattedFormatter(_Formatter):
    _format_line = LineFormatter().format

    def _handles(self, line):
        return line.startswith("| ") or line == "|"

    def format(self, lines):
        lines = [self._format_line(line[2:]) for line in lines]
        return "\n".join(["<pre>", *lines, "</pre>"])


class ListFormatter(_Formatter):
    _strip_lines = False
    _format_item = LineFormatter().format

    def _handles(self, line):
        return line.strip().startswith("- ") or line.startswith(" ") and self._lines

    def format(self, lines):
        items = [
            f"<li>{self._format_item(line)}</li>" for line in self._combine_lines(lines)
        ]
        return "\n".join(["<ul>", *items, "</ul>"])

    def _combine_lines(self, lines):
        current = []
        for line in lines:
            line = line.strip()
            if not line.startswith("- "):
                current.append(line)
                continue
            if current:
                yield " ".join(current)
            current = [line[2:].strip()]
        yield " ".join(current)
