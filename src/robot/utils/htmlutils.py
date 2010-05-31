#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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
  (\A|\ )                 # begin of line or space
  ["'(]* _?               # optionally any char "'( and optional begin of italic
)                         #
\*                        # start of bold
([^\ ].*?)                # no space and then anything (group 3)
\*                        # end of bold
(?=                       # start of postfix (non-capturing group)
  _? ["').,!?:;]*         # optional end of italic and any char "').,!?:;
  (\Z|\ )                 # end of line or space
)
''', re.VERBOSE)
_italic_re = re.compile('''
( (\A|\ ) ["'(]* )         # begin of line or space and opt. any char "'(
_                          # start of italic
([^\ _].*?)                # no space or underline and then anything
_                          # end of italic
(?= ["').,!?:;]* (\Z|\ ) ) # opt. any char "').,!?:; and end of line or space
''', re.VERBOSE)
_url_re = re.compile('''
( (\A|\ ) ["'([]* )         # begin of line or space and opt. any char "'([
(\w{3,9}://[\S]+?)          # url (protocol is any alphanum 3-9 long string)
(?= [])"'.,!?:;]* (\Z|\ ) ) # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE)


def html_escape(text, formatting=False):
    if not isinstance(text, basestring):
        text = unic(text)
    for name, value in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]:
        text = text.replace(name, value)

    ret = []
    table = _Table()
    hr = None

    for line in text.splitlines():
        if formatting and table.is_table_row(line):
            if hr:
                ret.append(hr)
                hr = None
            table.add_row(line)
        elif table.is_started():
            if _hr_re.match(line):
                hr = '<hr />\n'
                line = ''
            else:
                line = _format_line(line, True)
            ret.append(table.end() + line)
        elif formatting and _hr_re.match(line):
            hr = '<hr />\n'
        else:
            line = _format_line(line, formatting)
            if hr:
                line = hr + line
                hr = None
            ret.append(line)

    if table.is_started():
        ret.append(table.end())
    if hr:
        ret.append(hr)

    return '<br />\n'.join(ret)


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


def _format_line(line, formatting=False):
    if formatting:
        line = _bold_re.sub('\\1<b>\\3</b>', line)
        line = _italic_re.sub('\\1<i>\\3</i>', line)
    line = _url_re.sub(lambda res: _repl_url(res, formatting), line)
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
