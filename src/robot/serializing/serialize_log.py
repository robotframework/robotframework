from __future__ import with_statement

import re
import os
from robot import webcontent

PATH = os.path.dirname(webcontent.__file__)+os.path.sep
LOG_TEMPLATE = PATH + 'log.html'
REPORT_TEMPLATE = PATH + 'report.html'
JS_FILE_REGEXP = re.compile('src=\"([^\"]+)\"')

def serialize_log(test_output_datamodel, log_path, title=None):
    if log_path is None:
        return
    _build_file(log_path, test_output_datamodel, title, None, LOG_TEMPLATE)

def serialize_report(test_output_datamodel, report_path, title=None, background=None, logpath=None):
    if report_path is None:
        return
    _build_file(report_path, test_output_datamodel, title, _resolve_background_colors(background), REPORT_TEMPLATE)

def _build_file(outpath, test_output_datamodel, title, background, template):
    with open(outpath, 'w') as outfile:
        populator = _Populator(outfile, test_output_datamodel, title, background)
        with open(template, 'r') as templ:
            for line in templ:
                populator.line(line)

def _resolve_background_colors(color_str):
    if color_str and color_str.count(':') not in [1, 2]:
        #LOGGER.error("Invalid background color '%s'." % color_str)
        color_str = None
    if not color_str:
        color_str = '#99FF66:#FF3333'
    colors = color_str.split(':', 2)
    return colors if len(colors) == 3 else [colors[0], colors[0], colors[1]]


class _Populator(object):

    def __init__(self, log, test_output_datamodel, title, background):
        self._log = log
        self._test_output_datamodel = test_output_datamodel
        self._title = title
        self._parsing = self._normal_parsing
        self._backgrounds = {"/* BACKGROUND: critical pass */":     background[0] if background else None,
                             "/* BACKGROUND: non critical fail */": background[1] if background else None,
                             "/* BACKGROUND: critical fail */":     background[2] if background else None}

    def line(self, line):
        self._parsing(line)

    def _normal_parsing(self, line):
        for matcher in self._handlers:
            if matcher(line):
                self._handlers[matcher]()
                
        if self._is_begin_scripts(line):
            self._start_script()
        elif self._is_title_line_to_handle(line):
            self._write_title()
        elif self._is_background_line_to_handle(line):
            self._write_background(line)
        else:
            self._log.write(line)

    def _is_begin_scripts(self, line):
        return line == '<!-- BEGIN SCRIPTS -->\n'

    def _is_title_line_to_handle(self, line):
        return self._title is not None and line.startswith('<title>')

    def _write_title(self):
        self._log.write('<title>%s</title>\n' % self._title)

    def _is_background_line_to_handle(self, line):
        for marker in self._backgrounds:
            if marker in line:
                return True
        return False

    def _write_background(self, line):
        for marker in self._backgrounds:
            if marker in line:
                self._log.write("    background: %s;\n" % self._backgrounds[marker])

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
        return PATH + JS_FILE_REGEXP.search(line).group(1).replace('/', os.path.sep)

    def _write_js(self, js_file):
        with open(js_file, 'r') as js:
            for jsline in js:
                self._log.write(jsline)

if __name__ == '__main__':
    import jsparser
    jsparser.parse('output.xml', 'output.js')
    serialize_log('output.js', 'logjsx.html')