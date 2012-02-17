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


class UrlFormatter(object):
    _image_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    _url = re.compile('''
( (^|\ ) ["'([]* )         # begin of line or space and opt. any char "'([
(\w{3,9}://[\S]+?)         # url (protocol is any alphanum 3-9 long string)
(?= [])"'.,!?:;]* ($|\ ) ) # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE|re.MULTILINE)

    def __init__(self, formatting=False):
        self._formatting = formatting

    def format(self, text):
        return self._url.sub(self._repl_url, text) if '://' in text else text

    def _repl_url(self, match):
        pre = match.group(1)
        url = match.group(3).replace('"', '&quot;')
        if self._format_as_image(url):
            tmpl = '<img src="%s" title="%s" class="robotdoc">'
        else:
            tmpl = '<a href="%s">%s</a>'
        return pre + tmpl % (url, url)

    def _format_as_image(self, url):
        return self._formatting and url.lower().endswith(self._image_exts)


class HtmlFormatter(object):

    def __init__(self):
        self._rows = []
        self._formatters = (_TableFormatter(), _PreformattedBlockFormatter(),
                            _LineFormatter())
        self._current = None

    def format(self, text):
        for line in text.splitlines():
            self._process_line(line)
        self._end_current()
        return self.get_result()

    def _process_line(self, line):
        if self._current and self._current.add(line):
            return
        self._end_current()
        self._current = self._get_next(line)

    def _end_current(self):
        if self._current:
            self._rows.append(self._current.end())

    def _get_next(self, line):
        for formatter in self._formatters:
            if formatter.matcher(line):
                formatter.add(line)
                return formatter

    def get_result(self):
        return ''.join(self._rows).rstrip('\n')


class _LineFormatter(object):
    matcher = lambda self, line: True
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
    _ruler = re.compile('^-{3,} *$')

    def __init__(self):
        self._format_url = UrlFormatter(formatting=True).format
        self._result = None

    def add(self, line):
        if self._result is None:
            self._result = self.format(line)
            return True
        return False

    def end(self):
        result = self._result
        self._result = None
        if not result.startswith('<hr'):
            result += '\n'
        return result

    def format(self, line):
        if self._ruler.match(line):
            return '<hr class="robotdoc">'
        return self._format_url(self._format_italic(self._format_bold(line)))

    def _format_bold(self, line):
        return self._bold.sub('\\1<b>\\3</b>', line) if '*' in line else line

    def _format_italic(self, line):
        return self._italic.sub('\\1<i>\\3</i>', line) if '_' in line else line


class _TableFormatter(object):
    matcher = re.compile('^\s*\| (.* |)\|\s*$').match
    _line_splitter = re.compile(' \|(?= )')

    def __init__(self):
        self._rows = []
        self._line_formatter = _LineFormatter()

    def add(self, line):
        if self.matcher(line):
            text = line.strip()[1:-1]   # remove outer whitespace and pipes
            cells = [cell.strip() for cell in self._line_splitter.split(text)]
            self._rows.append(cells)
            return True
        return False

    def end(self):
        ret = self._format_table(self._rows)
        self._rows = []
        return ret

    def _format_table(self, rows):
        maxlen = max(len(row) for row in rows)
        table = ['<table class="robotdoc">']
        for row in rows:
            row += [''] * (maxlen - len(row))  # fix ragged tables
            table.append('<tr>')
            table.extend(['<td>%s</td>' % self._line_formatter.format(cell)
                          for cell in row])
            table.append('</tr>')
        table.append('</table>')
        return '\n'.join(table)


class _PreformattedBlockFormatter(object):
    matcher = re.compile('\s*\|( |$)').match

    def __init__(self):
        self._rows = []
        self._line_formatter = _LineFormatter()

    def add(self, line):
        if self.matcher(line):
            text = line.strip()[2:]
            self._rows.append(self._line_formatter.format(text))
            return True
        return False

    def end(self):
        ret = self._format_block()
        self._rows = []
        return ret

    def _format_block(self):
        return '\n'.join(['<pre class="robotdoc">'] + self._rows + ['</pre>'])
