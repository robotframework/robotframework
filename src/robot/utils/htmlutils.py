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

# TODO: cleanup!

_html_escape_re = re.compile('([&<>])')

def _html_escape_repl(match):
    return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[match.group(1)]


def html_escape(text, formatting=False):
    # TODO: Remove formatting attribute after RIDE does not use it anymore
    if formatting:
        return _ride_formatting(text)
    text = _html_escape(text).rstrip()
    if '://' not in text:
        return text
    return _UrlFormatter().format(text)

def _ride_formatting(text):
    return html_format(text).replace('\t', '&nbsp;'*8) \
                .replace('  ', ' &nbsp;').replace('\n', '<br>\n')

def _html_escape(text):
    return _html_escape_re.sub(_html_escape_repl, text)


def html_format(text):
    return _HtmlFormatter().format(text)


def html_attr_escape(attr):
    for name, value in [('&', '&amp;'), ('"', '&quot;'),
                        ('<', '&lt;'), ('>', '&gt;')]:
        attr = attr.replace(name, value)
    for wspace in ['\n', '\r', '\t']:
        attr = attr.replace(wspace, ' ')
    return attr


class _HtmlFormatter(object):
    _hr_re = re.compile('^-{3,} *$')

    def __init__(self):
        self._result = _Formatted()
        self._table = _TableFormatter()
        self._line_formatter = _LineFormatter()

    def format(self, text):
        text = _html_escape(text)
        for line in text.splitlines():
            self.add_line(line)
        return self.get_result()

    def add_line(self, line):
        if self._add_table_row(line):
            return
        if self._table.is_started():
            self._result.add(self._table.end(), join_after=False)
        if self._is_hr(line):
            self._result.add('<hr>', join_after=False)
            return
        self._result.add(self._line_formatter.format(line))

    def _add_table_row(self, row):
        if self._table.is_table_row(row):
            self._table.add_row(row)
            return True
        return False

    def _is_hr(self, line):
        return bool(self._hr_re.match(line))

    def get_result(self):
        if self._table.is_started():
            self._result.add(self._table.end())
        return self._result.get_result()


class _Formatted(object):

    def __init__(self):
        self._result = []
        self._joiner = ''

    def add(self, line, join_after=True):
        self._result.extend([self._joiner, line])
        self._joiner = '\n' if join_after else ''

    def get_result(self):
        return ''.join(self._result)


class _UrlFormatter(object):
    _image_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    _url = re.compile('''
( (^|\ ) ["'([]* )         # begin of line or space and opt. any char "'([
(\w{3,9}://[\S]+?)         # url (protocol is any alphanum 3-9 long string)
(?= [])"'.,!?:;]* ($|\ ) ) # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE|re.MULTILINE)

    def __init__(self, formatting=False):
        self._formatting = formatting

    def format(self, text):
        return self._url.sub(self._repl_url, text)

    def _repl_url(self, match):
        pre = match.group(1)
        url = match.group(3).replace('"', '&quot;')
        if self._format_as_image(url):
            tmpl = '<img src="%s" title="%s" style="border: 1px solid gray">'
        else:
            tmpl = '<a href="%s">%s</a>'
        return pre + tmpl % (url, url)

    def _format_as_image(self, url):
        return self._formatting and url.lower().endswith(self._image_exts)


class _LineFormatter(object):
    _bold = re.compile('''
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
    _italic = re.compile('''
( (^|\ ) ["'(]* )          # begin of line or space and opt. any char "'(
_                          # start of italic
([^\ _].*?)                # no space or underline and then anything
_                          # end of italic
(?= ["').,!?:;]* ($|\ ) )  # opt. any char "').,!?:; and end of line or space
''', re.VERBOSE)

    def __init__(self):
        self._url_formatter = _UrlFormatter(formatting=True).format

    def format(self, line):
        return self._format_url(self._format_italic(self._format_bold(line)))

    def _format_url(self, line):
        return self._url_formatter(line) if ':' in line else line

    def _format_bold(self, line):
        return self._bold.sub('\\1<b>\\3</b>', line) if '*' in line else line

    def _format_italic(self, line):
        return self._italic.sub('\\1<i>\\3</i>', line) if '_' in line else line


class _TableFormatter(object):
    _is_table_line = re.compile('^\s*\| (.* |)\|\s*$')
    _line_splitter = re.compile(' \|(?= )')

    def __init__(self):
        self._rows = []
        self._line_formatter = _LineFormatter()

    def is_table_row(self, row):
        return bool(self._is_table_line.match(row))

    def is_started(self):
        return bool(self._rows)

    def add_row(self, text):
        text = text.strip()[1:-1]   # remove outer whitespace and pipes
        cells = [cell.strip() for cell in self._line_splitter.split(text)]
        self._rows.append(cells)

    def end(self):
        ret = self._format_table(self._rows)
        self._rows = []
        return ret

    def _format_table(self, rows):
        maxlen = max(len(row) for row in rows)
        table = ['<table border="1" class="doc">']
        for row in rows:
            row += [''] * (maxlen - len(row))  # fix ragged tables
            table.append('<tr>')
            table.extend(['<td>%s</td>' % self._line_formatter.format(cell)
                          for cell in row])
            table.append('</tr>')
        table.append('</table>')
        return '\n'.join(table)
