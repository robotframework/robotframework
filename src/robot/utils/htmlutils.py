#  Copyright 2008 Nokia Siemens Networks Oyj
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

from robottypes import is_str


_html_entities = [ ('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;') ]
_attr_entities = [ ('"', '&quot;') ]
_table_line_re = re.compile('^\s*\| (.* |)\|\s*$')
_table_line_splitter = re.compile(' \|(?= )')

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
_bold_repl = r'\1<b>\3</b>'

_italic_re = re.compile('''
( (\A|\ ) ["'(]* )         # begin of line or space and opt. any char "'(
_                          # start of italic
([^\ _].*?)                # no space or underline and then anything
_                          # end of italic
(?= ["').,!?:;]* (\Z|\ ) ) # opt. any char "').,!?:; and end of line or space
''', re.VERBOSE)
_italic_repl = r'\1<i>\3</i>'

_link_re = re.compile('''
( (\A|\ ) ["'([]* )         # begin of line or space and opt. any char "'([
(\w{3,6}://[\S]+?)          # link (protocol is any alphanum 3-6 long string)
(?= [])"'.,!?:;]* (\Z|\ ) ) # opt. any char ])"'.,!?:; and end of line or space
''', re.VERBOSE)
_link_repl = r'\1<a href="\3">\3</a>'

_hr_re = re.compile('^-{3,} *$')
_hr_repl = '<hr />\n'


def html_escape(text, formatting=False):
    if not is_str(text):
        return text

    for name, value in _html_entities:
        text = text.replace(name, value)
    
    ret = []
    table = _Table()
    hr = None

    for line in text.splitlines():
        if formatting and _table_line_re.search(line) is not None:
            if hr is not None:
                ret.append(hr)
                hr = None
            table.add_row(line)
        elif table.is_started():
            if _hr_re.match(line):
                hr = _hr_repl
                line = ''
            else:
                line = _format_line(line, True)
            ret.append(table.end() + line)
        elif formatting and _hr_re.match(line):
            hr = _hr_repl
        else:
            line = _format_line(line, formatting)
            if hr is not None:
                line = hr + line
                hr = None
            ret.append(line)

    if table.is_started():
        ret.append(table.end())
    if hr is not None:
        ret.append(hr)
        
    return '<br />\n'.join(ret)


def html_attr_escape(attr):
    for name, value in _html_entities + _attr_entities + [('\n',' '), ('\t',' ')]:
        attr = attr.replace(name, value)
    return attr


class _Table:

    def __init__(self):
        self._rows = []

    def add_row(self, text):
        text = text.strip()[1:-1]   # remove outer whitespace and pipes
        cells = [ cell.strip() for cell in _table_line_splitter.split(text) ]
        self._rows.append(cells)

    def end(self):
        ret = _format_table(self._rows)
        self._rows = []
        return ret

    def is_started(self):
        return len(self._rows) > 0


_table_pre = ('<table border="1" style="border: 1px solid gray; '
              'background: transparent; '
              'border-collapse: collapse; '
              'font-size: 0.9em; '
              'empty-cells: show;">')
_cell_templ = '<td style="border: 1px solid gray; padding: 0.1em 0.3em;">%s</td>'

def _format_table(rows):
    maxlen = max([ len(row) for row in rows ])
    table = [ _table_pre ]
    for row in rows:
        row += [''] * (maxlen - len(row))  # fix ragged tables
        table.append('<tr>')
        table.extend([ _cell_templ % _format_line(cell, True) for cell in row ])
        table.append('</tr>')
    table.append('</table>')
    return '\n'.join(table)


def _format_line(line, formatting=False):
    # Handle _italic_ and *bold* only when asked to do so
    if formatting:
        line = _bold_re.sub(_bold_repl, line)
        line = _italic_re.sub(_italic_repl, line)
    
    # Always convert urls to clickable links
    line = _link_re.sub(_link_repl, line)
  
    # Replace tab with eight "hard" spaces and two "soft" spaces with one
    # "hard" and one "soft" space (preserves spaces but allows wrapping) 
    line = line.replace('\t', '&nbsp;'*8).replace('  ', ' &nbsp;')
    
    return line
