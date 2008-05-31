#!/usr/bin/env python

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


"""Tool for cleaning up Robot Framework test data.

Usage:  robotidy.py [options] inputfile outputfile
  or:   robotidy.py --inplace [options] inputfile [more input files]
  or:   robotidy.py --recursive [options] directory

Options:
 -I --inplace      Tidy given file(s) so that original file(s) are overwritten
                   When this option is used, it is possible to give multiple
                   files at once. Examples:
                   robotidy.py --inplace tests.html
                   robotidy.py --inplace --fixcomments *.html
 -R --recursive    Process given directory recursively. Files in the directory
                   are processed in place similarly as when '--inplace'
                   option is used.
 -X --fixcomments  Fix comments in the test data.
 -F --format html|tsv  
                   Format to use for output. Possible values are HTML and TSV.
                   If this option is not used, the format is got from the
                   extension of the output file.     
 -T --title text   Title to use in the test data. By default the title is got 
                   from the name of the output file. If the output file is
                   HTML the title is used with 'h1' and 'title' tags, and with
                   TSV it is simply printed before the first table. Possible
                   underscores in the given title are converted to spaces.
 -S --style path   Read styles from an external style sheet file and replace
                   default styles with them. If the path has a special value
                   'NONE', no styles are used. This setting is applicable only
                   when the output format is HTML.
 -h --help         Print this help.


This multipurpose tool has three main usages listed below.

1) Clean up the test data.

Source code created by most HTML editors is quite ugly. With this tool the 
source can be formatted nicely and it is even possible to specify a custon
style sheet. Additionally test data itself is cleaned up so that settings and
metadata is always in same predefined order.

Examples:
  robotidy.py messed_up_tests.html cleaned_tests.html 
  robotidy.py --style new_styles.css my_tests.html my_tests.html

2) Change format between HTML and TSV.

Robot Framework supports test data in HTML and TSV formats and this tools makes
changing between formats trivial. Input format is always determined from the
extension of the input file. Output format is also got from the output file
extension by default but it can also be set explicitly with '--format' option.

Examples:
  robotidy.py tests_in_html.html tests_in_tsv.tsv
  robotidy.py --format html tests.tsv tests.xxx

3) Fix comments.

Robot IDE is a great tool for editing the test data but at least currently it
totally ignores comments. This tool can be used to convert comments so that 
they are not lost when the test data is opened to the IDE. Comments in test 
case and user keyword tables are changed so that instead of '#' a built-in 
'Comment' keyword is used. In variable tables comments are converted to '@{#}'
or '${#}'. Comments in setting tables are not fixed. 

Examples:
  robotidy.py --fixcomments orig.html fixed.html
  robotidy.py --fixcomments --inplace *.html


Outputs are always written using UTF-8 encoding.
"""


import sys
import os
import glob

from robot.parsing import RawData, rawdatatables
from robot.output import SystemLogger
from robot.errors import DataError
from robot import utils


# Rows having comment in the first cell need to be handled differently because
# otherwise they'd start a new tc or uk. Such row are simply indented one column
# right if they are after first real tc/uk has started. If there is a comment
# before first element, a new tc/uk is created with name '#' and it's contents
# are moved to the firts real tc/uk later if comments are fixed. 
def _monkey_patched_add_row(self, name, data):
    if name.startswith('#'):
        data = [name] + data
        if self._item is not None:
            name = ''
        else:
            name = '#'  
    self._orig_add_row(name, data)

rawdatatables.ComplexTable._orig_add_row = rawdatatables.ComplexTable._add_row
rawdatatables.ComplexTable._add_row = _monkey_patched_add_row

# Support "x in normdict" in pre Robot 1.8.3 versions
utils.NormalizedDict.__contains__ = utils.NormalizedDict.has_key

# Order of names is important because settings/metadata are written in this
# order (except for 'Teardown' and 'Return')
_import_names = ['Variables', 'Resource', 'Library']
_setting_names = ['Documentation', 'Suite Setup', 'Suite Teardown', 'Test Setup',
                  'Test Teardown', 'Default Tags', 'Force Tags', 'Test Timeout']
_test_names = ['Documentation', 'Setup', 'Teardown', 'Tags', 'Timeout']
_keyword_names = ['Arguments', 'Documentation', 'Return', 'Timeout']

def _create_mapping(names):
    mapping = utils.NormalizedDict()
    for name in names:
        mapping[name] = name
    if 'Documentation' in names:
        mapping['Document'] = 'Documentation'
    return mapping
    
_import_map = _create_mapping(_import_names)
_setting_map = _create_mapping(_setting_names)
_test_map = _create_mapping(_test_names)
_keyword_map = _create_mapping(_keyword_names)

_valid_extensions = ['TSV','HTML','HTM','XHTML']

_default_styles = '''
<style type="text/css">
html {
  font-family: Arial,Helvetica,sans-serif;
  background-color: white;
  color: black;
}
table {
  border-collapse: collapse;
  empty-cells: show;
  margin: 1em 0em;
  border: 0.1em solid black;
}
th, td {
  border-style: solid;
  border-width: 0.05em 0.1em;
  border-color: black;
  padding: 0.1em 0.2em;
  height: 1.5em;
}
th {
  background-color: rgb(192, 192, 192);
  color: black;
  border-width: 0.1em;
  font-weight: bold;
  text-align: center;
  text-transform: capitalize;
  letter-spacing: 0.1em;
}
.col_name, .col_value {
  width: 12em;
}
td.col_name {
  background-color: rgb(240, 240, 240);
  text-transform: capitalize;
  letter-spacing: 0.1em;
}
</style>
'''

SYSLOG = SystemLogger()


def process_file(infile, outfile, opts):
    if outfile is not None:
        print '%s -> %s' % (infile, outfile)
    else:
        print infile
        outfile = infile
    if not os.path.isfile(infile):
        SYSLOG.error("'%s' is not a regular file" % infile)
        return
    data = TestData(infile, opts['fixcomments'])
    data.serialize(outfile, opts['format'], opts['title'], opts['style'])

    
def process_directory(indir, otps):
    for item in os.listdir(indir):
        path = os.path.join(indir, item)
        if os.path.isdir(path):
            process_directory(path, otps)
        elif os.path.isfile(path):
            process_file(path, None, opts)
            

class TestData:
    
    def __init__(self, path, fix_comments=False):
        if not os.path.isfile(path) or os.path.splitext(path)[1][1:].upper() \
                not in _valid_extensions:
            raise DataError("Input format must be either HTML or TSV.")
        raw = RawData(path, SYSLOG, strip_comments=False, process_curdir=False)
        if raw.is_empty():
            raise DataError("'%s' contains no test data" % path)
        self.settings = Settings(raw.settings, fix_comments)
        self.variables = Variables(raw.variables, fix_comments)
        self.testcases = TestCases(raw.testcases, fix_comments)
        self.keywords = UserKeywords(raw.keywords, fix_comments)

    def serialize(self, path, format=None, title=None, style=None):
        serializer = self._get_serializer(path, format, title, style)
        self.settings.serialize(serializer)
        self.variables.serialize(serializer)
        self.testcases.serialize(serializer)
        self.keywords.serialize(serializer)
        serializer.close()
        
    def _get_serializer(self, path, format, title, style):
        if format is None:
            format = os.path.splitext(path)[1][1:]
        format = format.upper()
        if format not in _valid_extensions:
            raise DataError("Invalid output format '%s'. Only HTML and TSV "
                            "are supported." % format)
        title = self._get_title(title, path)
        if format == 'TSV':
            return TsvSerializer(open(path, 'wb'), title)
        return HtmlSerializer(open(path, 'wb'), title, self._get_style(style))

    def _get_title(self, given_title, path):
        if given_title is not None:
            return utils.printable_name(given_title.replace('_', ' '))
        return utils.printable_name_from_path(path)
    
    def _get_style(self, given_style_path):
        if given_style_path is None:
            return _default_styles
        if given_style_path.upper() == 'NONE':
            return ''
        try:
            return open(given_style_path).read()
        except IOError, err:
            raise DataError("Opening style sheet file '%s' failed: %s" 
                            % (given_style_path, str(err)))
      

class Settings:

    def __init__(self, raw_settings, fix_comments):
        self._imports = dict([ (name, []) for name in _import_names ])
        self._settings = dict([ (name, None) for name in _setting_names ])
        self._metadata = {}
        self._comments = []
        for item in raw_settings:
            if item.name in _import_map:
                self._imports[_import_map[item.name]].append(item.value)
            elif item.name in _setting_map:
                if self._settings[_setting_map[item.name]] is None:
                    self._settings[_setting_map[item.name]] = []
                self._settings[_setting_map[item.name]].extend(item.value)
            elif item.name.upper().startswith('META:'):
                self._metadata[item.name[5:].strip()] = item.value
            elif item.name.startswith('#'):
                self._comments.append([item.name] + item.value)
            elif item.name == '':
                self._comments.append(['#'] + item.value)
            else:
                SYSLOG.error("Invalid setting '%s'" % item.name)
        if self._comments and fix_comments:
            SYSLOG.warn('Comments in setting table are not fixed.')

    def serialize(self, serializer):
        serializer.start_settings()
        for name in _import_names:
            for value in self._imports[name]:
                serializer.setting(name, value)
        for name in _setting_names:
            serializer.setting(name, self._settings[name])
        for name, value in sorted(self._metadata.items()):
            serializer.setting('Meta: '+name, value)
        if self._comments:
            serializer.row(['###', 'Comments are not supported in this table.',
                            'Original comments below.'])
            for comment in self._comments:
                serializer.row(comment)
        serializer.end_settings()
        
        
def _split_comment(data):
    has_data = False
    for index, item in enumerate(data):
        if item.startswith('#'):
            if has_data:
                return data[:index], data[index:]
            else:
                return None, data
        if item != '':
            has_data = True
    return data, None
                
        
class Variables:
    
    def __init__(self, raw_vars, fix_comments):
        if not fix_comments:
            self._vars = [ [item.name] + item.value for item in raw_vars ]
        else:
            self._vars = self._fix_comments(raw_vars)
            
    def _fix_comments(self, raw_vars):
        fixed = []
        for item in raw_vars:
            var, comm = _split_comment([item.name]+item.value)
            if var is not None:
                fixed.append(var)
            if comm is not None:
                comm = self._fix_comment(comm)
                if var is not None:
                    comm.append('(Comment moved from the end of the previous variable.)')
                fixed.append(comm)
        return fixed
                
    def _fix_comment(self, data):
        data[0] = data[0][1:].strip()
        if data[0] == '':
            data.pop(0)
        name = len(data) > 1 and '@{#}' or '${#}'
        return [name] + [ utils.escape(item) for item in data ]

    def serialize(self, serializer):
        serializer.start_variables()
        for data in self._vars:
            serializer.variable(data[0], data[1:])
        serializer.end_variables()
     

class Keyword:

    def __init__(self, data):
        self._data = data
            
    def serialize(self, serializer):
        serializer.keyword(self._data)


class FixedKeyword:

    def __init__(self, data):
        self._kw_data, self._comm_data = _split_comment(data)
        if self._comm_data is not None:
            self._comm_data = self._fix_comment(self._comm_data)
            if self._kw_data is not None:
                self._comm_data.append('(Comment moved from the end of the '
                                       'previous keyword.)')

    def _fix_comment(self, data):
        # Possible one leading empty cell must be preserved because otherwise
        # comments in blocks (FOR, PARALLEL) would break. Having more than one
        # leading empty cells is not possible so they are removed.
        # If there are leading empty cells outside blocks executing tests will
        # fail. Checking are we in a block would be rather big task so let's
        # just hope this doesn't happen too often...
        leading_empty = 0
        while data[0] == '':
            data.pop(0)
            leading_empty = 1
        data[0] = data[0][1:].strip()  # Remove '#'
        if data[0] == '':
            data.pop(0)
        return ['']*leading_empty + ['Comment'] + [ utils.escape(item) for item in data ]
    
    def serialize(self, serializer):
        if self._kw_data is not None:
            serializer.keyword(self._kw_data)
        if self._comm_data is not None:
            serializer.keyword(self._comm_data)


class _TcUkBase:
    
    def __init__(self, raw):
        self.name = raw.name
        self._keywords = [ self._kw_class(kw) for kw in raw.keywords ]
        self._metadata = dict([ (name, None) for name in self._names ]) 
        for meta in raw.metadata:
            self._add_meta(meta)
        
    def _add_meta(self, raw):
        if raw.name not in self._mapping:
            SYSLOG.error("Invalid metadata '%s'" % raw.name)
            return
        if self._metadata[self._mapping[raw.name]] is None:
            self._metadata[self._mapping[raw.name]] = []
        self._metadata[self._mapping[raw.name]].extend(raw.value)
            
    def serialize(self, serializer):
        serializer.start_tc_or_kw(self.name)
        for name in self._names:
            if name != self._post_meta:
                serializer.metadata(name, self._metadata[name])
        for kw in self._keywords:
            kw.serialize(serializer)
        serializer.metadata(self._post_meta, self._metadata[self._post_meta])            
        serializer.end_tc_or_kw()


class _TcInfo:
    _names = _test_names
    _mapping = _test_map
    _post_meta = 'Teardown'

class _UkInfo:
    _names = _keyword_names
    _mapping = _keyword_map
    _post_meta = 'Return'
    
class TestCase(_TcUkBase, _TcInfo):
    _kw_class = Keyword
    
class FixedTestCase(_TcUkBase, _TcInfo):
    _kw_class = FixedKeyword
    
class UserKeyword(_TcUkBase, _UkInfo):
    _kw_class = Keyword
    
class FixedUserKeyword(_TcUkBase, _UkInfo):
    _kw_class = FixedKeyword


class _TcsUksBase:
    
    def __init__(self, raw_items, item_class, fix_comments):
        self._items = [ item_class(item) for item in raw_items ]
        if fix_comments and self._items and self._items[0].name.startswith('#'):
            self._fix_comments_before_first_item()

    def _fix_comments_before_first_item(self):
        comment = self._items.pop(0)
        if not self._items:
            SYSLOG.warn('Comments in otherwise empty test case or keyword table are ignored.')
            return
        for item in reversed(comment._keywords):
            item._comm_data.append('(Comment originally before first item in this table.)')
            self._items[0]._keywords.insert(0, item)


class TestCases(_TcsUksBase):
    
    def __init__(self, raw_items, fix_comments):
        tc_class = fix_comments and FixedTestCase or TestCase
        _TcsUksBase.__init__(self, raw_items, tc_class, fix_comments)
    
    def serialize(self, serializer):
        if self._items:
            serializer.start_testcases()
            for tc in self._items:
                tc.serialize(serializer)
            serializer.end_testcases()


class UserKeywords(_TcsUksBase):

    def __init__(self, raw_items, fix_comments):
        uk_class = fix_comments and FixedUserKeyword or UserKeyword
        _TcsUksBase.__init__(self, raw_items, uk_class, fix_comments)
    
    def serialize(self, serializer):
        serializer.start_keywords()
        for uk in self._items:
            uk.serialize(serializer)
        serializer.end_keywords()


class _SerializerBase:
    
    def start_settings(self):
        self._start_table(['Setting', 'Value'], self._setvar_width)
        
    def start_variables(self):
        self._start_table(['Variable', 'Value'], self._setvar_width)

    def start_testcases(self):
        self._start_table(['Test Case', 'Action', 'Argument'], self._tckw_width)
    
    def start_keywords(self):
        self._start_table(['Keyword', 'Action', 'Argument'], self._tckw_width)

    def end_settings(self):
        self._empty_row()
        self._end_table()

    end_variables = end_settings
        
    def end_testcases(self):
        if self._table_is_empty:
            self._empty_row()
        self._end_table()

    end_keywords = end_testcases

    def start_tc_or_kw(self, name):
        self._start_row()
        self._cell(name)
        self._tckw_is_empty = True

    def end_tc_or_kw(self):
        if self._tckw_is_empty:
            self._row([], indent=1, started=True)
        self._empty_row()             
    
    def metadata(self, name, value):
        if value is not None:
            self._row(['[%s]'%name] + value, 1, self._tckw_is_empty) 
    
    def keyword(self, data):
        # Handle indented keywords used with FOR and PARALLEL
        if data[0] == '':
            data = data[1:]
            indent = 2
        else:
            indent = 1
        self._row(data, indent, self._tckw_is_empty)
    
    def setting(self, name, value):
        if value is not None:
            self._row([name] + value)
        
    variable = setting

    def row(self, data, indent=0):
        self._row(data, indent)

    def _start_table(self, headers, width):
        headers = headers + headers[-1:] * (width-len(headers))
        self._start_row()
        for name in headers:
            self._cell(name, header=True)
        self._end_row()
        self._width = width
        self._table_is_empty = True

    def _row(self, data, indent=0, started=False):
        if not started:
            self._start_row()
            self._empty_cell(indent)
        index = indent
        for item in data:
            if index > indent and index % self._width == 0:
                self._end_row()
                self._start_row()
                self._empty_cell(indent)
                self._cell('...')
                index = indent + 1
            self._cell(item)
            index += 1
        while index % self._width != 0:
            self._empty_cell()
            index += 1
        self._end_row()
        self._table_is_empty = self._tckw_is_empty = False

    def _cell(self, data, header=False):
        pass

    def _empty_row(self):
        self._row([''] * self._width)
        
    def _empty_cell(self, count=1):
        for i in range(count):
            self._cell('')

    def _end_table(self):
        pass

    def _start_row(self):
        pass

    def _end_row(self):
        pass

    def close(self):
        pass


class HtmlSerializer(_SerializerBase):
    
    _setvar_width = 4
    _tckw_width = 6
    
    def __init__(self, output, title, style):
        output.write('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta name="generator" content="robotidy.py" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
%(STYLE)s
<title>%(TITLE)s</title>
</head>
<body>
<h1>%(TITLE)s</h1>
''' % {'STYLE': style.strip(), 'TITLE': title})
        self._writer = utils.HtmlWriter(output)

    def close(self):
        self._writer.end_elements(['body','html'])
        self._writer.output.close()

    def _start_table(self, headers, width):
        self._writer.start_element('table', {'border':'1'})
        _SerializerBase._start_table(self, headers, width)

    def _end_table(self):
        self._writer.end_element('table')

    def _start_row(self):
        self._writer.start_element('tr')
        self._row_empty = True
        
    def _end_row(self):
        self._writer.end_element('tr')

    def _cell(self, data, header=False):
        elem = header and 'th' or 'td'
        cls = self._row_empty and 'col_name' or 'col_value'
        self._writer.whole_element(elem, data, {'class': cls})
        self._row_empty = False


class TsvSerializer(_SerializerBase):
    
    _setvar_width = 8 
    _tckw_width = 8
    
    def __init__(self, output, title):
        output.write(' '.join(title.upper()) + '\n\n')
        self._output = output

    def close(self):
        self._output.close()

    def _end_table(self):
        self._output.write('\n')

    def _end_row(self):
        self._output.write('\n')

    def _cell(self, data, header=False):
        if header:
            data = '*%s*' % data
        self._output.write(data.encode('UTF-8') + '\t')


if __name__ == '__main__':
    try:
        ap = utils.ArgumentParser(__doc__)
        opts, args = ap.parse_args(sys.argv[1:])
        if opts['help']:
            print __doc__
        elif opts['inplace']:
            if len(args) == 0:
                raise DataError('--inplace requires at least one argument')
            for pattern in args:
                paths = glob.glob(pattern)
                if not paths:
                    paths = [pattern]  # no match - error handled later
                for path in paths:
                    process_file(path, None, opts)
        elif opts['recursive']:
            if len(args) != 1:
                raise DataError('--recursive requires exactly one argument')
            if not os.path.isdir(args[0]):
                raise DataError('Parameter to --recursive must be a directory')
            process_directory(args[0], opts)
        else:
            if len(args) != 2:
                raise DataError('Both input and output files must be given')
            process_file(args[0], args[1], opts)
    except KeyboardInterrupt:
        pass
    except:
        SYSLOG.error(utils.get_error_message())
        print '\nUse --help to get usage information.'
