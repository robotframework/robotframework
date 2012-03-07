#  Copyright 2008-2012 Nokia Siemens Networks Oyj
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


class LinkFormatter(object):
    _image_exts = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    _link = re.compile('(\[.+?\|.*?\])')
    _url = re.compile('''
((^|\ ) ["'([]*)           # begin of line or space and opt. any char "'([
(\w{3,9}://[\S]+?)         # url (protocol is any alphanum 3-9 long string)
(?=[])"'.,!?:;]* ($|\ ))   # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE|re.MULTILINE)

    def format_url(self, text):
        return self._format_url(text, format_as_image=False)

    def _format_url(self, text, format_as_image=True):
        if '://' not in text:
            return text
        return self._url.sub(partial(self._replace_url, format_as_image), text)

    def _replace_url(self, format_as_image, match):
        pre = match.group(1)
        url = match.group(3)
        if format_as_image and self._is_image(url):
            return pre + self._get_image(url)
        return pre + self._get_link(url)

    def _get_image(self, src, title=None):
        return '<img src="%s" title="%s" class="robotdoc">' \
                % (self._quot(src), self._quot(title or src))

    def _get_link(self, href, content=None):
        return '<a href="%s">%s</a>' % (self._quot(href), content or href)

    def _quot(self, attr):
        return attr.replace('"', '&quot;')

    def format_link(self, text):
        return ''.join(formatter(token) for formatter, token in
                       zip(cycle([self._format_url, self._format_link]),
                           self._link.split(text)))

    def _format_link(self, text):
        return self._link.sub(self._replace_link, text)

    def _replace_link(self, match):
        link, content = [t.strip() for t in match.group()[1:-1].split('|', 1)]
        if self._is_image(content):
            content = self._get_image(content, link)
        elif self._is_image(link):
            return self._get_image(link, content)
        return self._get_link(link, content)

    def _is_image(self, text):
        return text.lower().endswith(self._image_exts)


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
        self.handles = formatter.handles


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
    handles = lambda self, line: True
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
        self._format_link = LinkFormatter().format_link

    def format(self, line):
        return self._format_link(self._format_italic(self._format_bold(line)))

    def _format_bold(self, line):
        return self._bold.sub('\\1<b>\\3</b>', line) if '*' in line else line

    def _format_italic(self, line):
        return self._italic.sub('\\1<i>\\3</i>', line) if '_' in line else line


class RulerFormatter(object):
    handles = re.compile('^-{3,} *$').match
    newline = ''

    def format(self, line):
        return '<hr class="robotdoc">'


class TableFormatter(object):
    handles = re.compile('^\s*\| (.* |)\|\s*$').match
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
    handles = re.compile('\s*\|( |$)').match
    _format_line = LineFormatter().format

    def pre_format(self, line):
        return line.strip()[2:]

    def format(self, lines):
        lines = [self._format_line(line) for line in lines]
        return '\n'.join(['<pre class="robotdoc">'] + lines + ['</pre>'])
