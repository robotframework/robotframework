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
        self._collectors = (BlockCollector(self._rows, TableFormatter()),
                            BlockCollector(self._rows, PreformattedFormatter()),
                            LineCollector(self._rows, RulerFormatter()),
                            LineCollector(self._rows, LineFormatter()))
        self._current_block = None

    def format(self, text):
        for line in text.splitlines():
            self._process_line(line)
        self._end_current_block()
        return ''.join(self._rows).rstrip('\n')

    def _process_line(self, line):
        if self._current_block and self._current_block.handles(line):
            self._current_block.add(line)
            return
        self._end_current_block()
        collector = self._find_collector(line)
        collector.add(line)
        self._current_block = collector if collector.is_block else None

    def _end_current_block(self):
        if self._current_block:
            self._current_block.end()

    def _find_collector(self, line):
        for collector in self._collectors:
            if collector.handles(line):
                return collector


class _Collector(object):

    def __init__(self, result, formatter):
        self._result = result
        self._formatter = formatter
        self.handles = re.compile(formatter.pattern).match


class LineCollector(_Collector):
    is_block = False

    def add(self, line):
        self._result.append(self._formatter.format(line) +
                            self._formatter.newline)


class BlockCollector(_Collector):
    is_block = True

    def __init__(self, result, formatter):
        _Collector.__init__(self, result, formatter)
        self._lines = []

    def add(self, line):
        self._lines.append(self._formatter.pre_format(line))

    def end(self):
        self._result.append(self._formatter.format(self._lines))
        self._lines = []


class LineFormatter(object):
    pattern = '.*'
    newline = '\n'
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
        self._format_url = UrlFormatter(formatting=True).format

    def format(self, line):
        return self._format_url(self._format_italic(self._format_bold(line)))

    def _format_bold(self, line):
        return self._bold.sub('\\1<b>\\3</b>', line) if '*' in line else line

    def _format_italic(self, line):
        return self._italic.sub('\\1<i>\\3</i>', line) if '_' in line else line


class RulerFormatter(object):
    pattern = '^-{3,} *$'
    newline = ''

    def format(self, line):
        return '<hr class="robotdoc">'


class TableFormatter(object):
    pattern = '^\s*\| (.* |)\|\s*$'
    _line_splitter = re.compile(' \|(?= )')
    _format_cell = LineFormatter().format

    def pre_format(self, line):
        line = line.strip()[1:-1]   # remove outer whitespace and pipes
        return [cell.strip() for cell in self._line_splitter.split(line)]

    def format(self, lines):
        maxlen = max(len(row) for row in lines)
        table = ['<table class="robotdoc">']
        for line in lines:
            line += [''] * (maxlen - len(line))  # fix ragged tables
            table.append('<tr>')
            table.extend(['<td>%s</td>' % self._format_cell(cell)
                          for cell in line])
            table.append('</tr>')
        table.append('</table>')
        return '\n'.join(table)


class PreformattedFormatter(object):
    pattern = '\s*\|( |$)'
    _format_line = LineFormatter().format

    def pre_format(self, line):
        return line.strip()[2:]

    def format(self, lines):
        lines = [self._format_line(line) for line in lines]
        return '\n'.join(['<pre class="robotdoc">'] + lines + ['</pre>'])
