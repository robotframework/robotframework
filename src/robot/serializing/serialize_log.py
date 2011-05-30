from __future__ import with_statement

import re
import os
from robot import webcontent

PATH = os.path.dirname(webcontent.__file__)+'/'
LOG_TEMPLATE = PATH + 'log.html'
JS_FILE_REGEXP = re.compile('src=\"([^\"]+)\"')

def serialize_log(test_output_datamodel, log_path, title=None):
    if log_path is None:
        return
    _build_log_file(log_path, test_output_datamodel, title)

def _build_log_file(log_path, test_output_datamodel, title):
    with open(log_path, 'w') as log:
        populator = _Populator(log, test_output_datamodel, title)
        with open(LOG_TEMPLATE, 'r') as template:
            for line in template:
                populator.line(line)

class _Populator(object):

    def __init__(self, log, test_output_datamodel, title):
        self._log = log
        self._test_output_datamodel = test_output_datamodel
        self._title = title
        self._parsing = self._normal_parsing

    def line(self, line):
        self._parsing(line)

    def _normal_parsing(self, line):
        if self._is_begin_scripts(line):
            self._start_script()
        elif self._is_title_line_to_handle(line):
            self._write_title()
        else:
            self._log.write(line)

    def _is_begin_scripts(self, line):
        return line == '<!-- BEGIN SCRIPTS -->\n'

    def _is_title_line_to_handle(self, line):
        return self._title is not None and line.startswith('<title>')

    def _write_title(self):
        self._log.write('<title>%s</title>\n' % self._title)

    def _in_script(self, line):
        if self._is_end_scripts(line):
            self._end_script()
        elif self._is_output_js(line):
            self._write_output_js()
        else:
            self._write_lines_js(line)

    def _is_end_scripts(self, line):
        return line == '<!-- END SCRIPTS -->\n'

    def _end_script(self):
        self._log.write('</script>\n')
        self._parsing = self._normal_parsing

    def _is_output_js(self, line):
        return line.startswith('<!-- OUTPUT JS -->')

    def _write_output_js(self):
        self._test_output_datamodel.write_to(self._log)

    def _write_lines_js(self, line):
        self._write_js(self._parse_js_file_name(line))

    def _start_script(self):
        self._log.write('<script type="text/javascript">\n')
        self._parsing = self._in_script

    def _parse_js_file_name(self, line):
        return PATH + JS_FILE_REGEXP.search(line).group(1)

    def _write_js(self, js_file):
        with open(js_file, 'r') as js:
            for jsline in js:
                self._log.write(jsline)

if __name__ == '__main__':
    import jsparser
    jsparser.parse('output.xml', 'output.js')
    serialize_log('output.js', 'logjsx.html')