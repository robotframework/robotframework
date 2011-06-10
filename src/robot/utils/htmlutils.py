#  Copyright 2008-2011 Nokia Siemens Networks Oyj
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
import os.path

from unic import unic


_hr_re = re.compile('^-{3,} *$')
_bold_re = re.compile('''
(                         # prefix (group 1)
  (^|\ )                  # begin of line or space
  ["'(]* _?               # optionally any char "'( and optional begin of italic
)                         #
\*                        # start of bold
([^\ ].*?)                # no space and then anything (group 3)
\*                        # end of bold
(?=                       # start of postfix (non-capturing group)
  _? ["').,!?:;]*         # optional end of italic and any char "').,!?:;
  ($|\ )                  # end of line or space
)
''', re.VERBOSE)
_italic_re = re.compile('''
( (^|\ ) ["'(]* )          # begin of line or space and opt. any char "'(
_                          # start of italic
([^\ _].*?)                # no space or underline and then anything
_                          # end of italic
(?= ["').,!?:;]* ($|\ ) )  # opt. any char "').,!?:; and end of line or space
''', re.VERBOSE)
_url_re = re.compile('''
( (^|\ ) ["'([]* )         # begin of line or space and opt. any char "'([
(\w{3,9}://[\S]+?)         # url (protocol is any alphanum 3-9 long string)
(?= [])"'.,!?:;]* ($|\ ) ) # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE)


def html_escape(text, formatting=False, replace_whitespace=True):
    text = unic(text)
    formatter = _HtmlStringFormatter(formatting, replace_whitespace)
    for line in text.splitlines():
        formatter.add(line)
    return formatter.result()


class _HtmlStringFormatter(object):

    def __init__(self, formatting, replace_whitespace):
        self._formatting = formatting
        self._replace = replace_whitespace
        self._result = _Formatted(replace_whitespace)
        self._table = _Table()

    def add(self, line):
        line = self._escape_gt_lt_amp(line)
        if self._add_table_row(line):
            return
        if self._table.is_started():
            self._result.add(self._table.end(), join_after=False)
        if self._is_hr(line):
            self._result.add('<hr />\n', join_after=False)
            return
        self._result.add(_format_line(line, self._formatting, self._replace))

    def _add_table_row(self, row):
        if self._formatting and self._table.is_table_row(row):
            self._table.add_row(row)
            return True
        return False

    def _is_hr(self, line):
        return self._formatting and _hr_re.match(line)

    def result(self):
        if self._table.is_started():
            self._result.add(self._table.end())
        return self._result.result()

    def _escape_gt_lt_amp(self, text):
        for name, value in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]:
            text = text.replace(name, value)
        return text


class _Formatted(object):

    def __init__(self, replace_whitespace):
        self._newline = '<br />\n' if replace_whitespace else '\n'
        self._result = []
        self._joiner = ""

    def add(self, line, join_after=True):
        self._result += [self._joiner]
        self._joiner = self._newline if join_after else ""
        self._result += [line]

    def result(self):
        return ''.join(self._result)


def _format_line(line, formatting=False, replace_whitespace=True):
    if formatting:
        line = _bold_re.sub('\\1<b>\\3</b>', line)
        line = _italic_re.sub('\\1<i>\\3</i>', line)
    line = _url_re.sub(lambda res: _repl_url(res, formatting), line)
    return _replace_whitespace(line) if replace_whitespace else line

def _replace_whitespace(line):
    # Replace a tab with eight "hard" spaces, and two "soft" spaces with one
    # "hard" and one "soft" space (preserves spaces but allows wrapping)
    return line.replace('\t', '&nbsp;'*8).replace('  ', ' &nbsp;')

def _repl_url(res, formatting):
    pre = res.group(1)
    url = res.group(3).replace('"', '&quot;')
    if formatting and os.path.splitext(url)[1].lower() \
           in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
        return '%s<img src="%s" title="%s" style="border: 1px solid gray" />' % (pre, url, url)
    return '%s<a href="%s">%s</a>' % (pre, url, url)

def html_attr_escape(attr):
    for name, value in [('&', '&amp;'), ('"', '&quot;'),
                        ('<', '&lt;'), ('>', '&gt;')]:
        attr = attr.replace(name, value)
    for wspace in ['\n', '\r', '\t']:
        attr = attr.replace(wspace, ' ')
    return attr


class _Table:

    _is_line = re.compile('^\s*\| (.* |)\|\s*$')
    _line_splitter = re.compile(' \|(?= )')

    def __init__(self):
        self._rows = []

    def is_table_row(self, row):
        return self._is_line.match(row) is not None

    def add_row(self, text):
        text = text.strip()[1:-1]   # remove outer whitespace and pipes
        cells = [ cell.strip() for cell in self._line_splitter.split(text) ]
        self._rows.append(cells)

    def end(self):
        ret = self._format(self._rows)
        self._rows = []
        return ret

    def is_started(self):
        return len(self._rows) > 0

    def _format(self, rows):
        maxlen = max([ len(row) for row in rows ])
        table = ['<table border="1" class="doc">']
        for row in rows:
            row += [''] * (maxlen - len(row))  # fix ragged tables
            table.append('<tr>')
            table.extend([ '<td>%s</td>' % _format_line(cell, True)
                           for cell in row ])
            table.append('</tr>')
        table.append('</table>\n')
        return '\n'.join(table)
