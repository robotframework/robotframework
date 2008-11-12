import sys
import time

from robot.running import TestSuite
from robot.conf import RobotSettings
from robot.output import SystemLogger
from robot.running.namespace import _VariableScopes
from robot.serializing.serializer import LogSuiteSerializer
from robot.serializing import templates
from robot.serializing.templating import Namespace, Template
from robot import utils


class MySerializer(LogSuiteSerializer):
    
    def __init__(self, output, suite):
        self._writer = utils.HtmlWriter(output)
        self._idgen = utils.IdGenerator()
        self._suite_level = 0
        self._suite = suite
    
    def start_suite(self, suite):
        suite._init_suite(_VariableScopes(self._suite, None))
        LogSuiteSerializer.start_suite(self, suite)
    
    def start_test(self, test):
        test._init_test(_VariableScopes(self._suite, None))
        LogSuiteSerializer.start_test(self, test)
    
    def _is_element_open(self, item):
        return False
    
    def _write_suite_or_test_name(self, item, type_):
        self._writer.start_elements(['tr', 'td'])
        self._writer.whole_element('a', 'Expand All', {'class': 'expand', 
                                   'href': "javascript:expand_all_children('%s')" % item.id})
        self._write_folding_button(item)
        label = type_ == 'suite' and 'TEST&nbsp;SUITE: ' or 'TEST&nbsp;CASE: '
        self._writer.whole_element('span', label, escape=False)
        self._writer.whole_element('a', item.name, 
                                   {'name': '%s_%s' % (type_, item.mediumname),
                                    'class': 'name', 'title': item.longname})
        self._writer.end_elements(['td', 'tr'])
        
    def _write_suite_metadata(self, suite):
        self._start_suite_or_test_metadata(suite)
        for name, value in suite.get_metadata(html=True):
            self._write_metadata_row(name, value, escape=False, write_empty=True)
        for title, values in [ ('Critical Tags', suite.critical.tags),
                               ('Non-Critical Tags', suite.critical.nons),
                               ('Included Suites', suite.filtered.suites), 
                               ('Included Tests', suite.filtered.tests),
                               ('Included Tags', suite.filtered.incls), 
                               ('Excluded Tags', suite.filtered.excls) ]:
            self._write_metadata_row(title, ', '.join(values), escape=False)
        self._writer.end_element('table')
    
    def _write_test_metadata(self, test):
        self._start_suite_or_test_metadata(test)
        self._write_metadata_row('Tags', ', '.join(test.tags))
        crit = test.critical == 'yes' and 'critical' or 'non-critical'
        self._writer.end_element('table')
        
        
def produce(sources):
    suite = TestSuite([sources], RobotSettings(), SystemLogger())
    outfile = open('test.html', 'w')
    serializer = MySerializer(outfile, suite)
    ttuple = time.localtime()
    str_time = '%s %s' % (utils.format_time(ttuple, daytimesep='&nbsp;'),
                          utils.get_diff_to_gmt())
    int_time = long(time.mktime(ttuple))
    namespace = Namespace(gentime_str=str_time, gentime_int=int_time, 
                          version=utils.get_full_version('RoboPlan'), 
                          suite=suite, title='Test plan for %s' % suite.name)
    tmpl = Template(template=templates.LOG)
    tmpl.generate(namespace, outfile)
    suite.serialize(serializer)
    outfile.write('</body>\n</html>\n')
    outfile.close()

if __name__ == '__main__':
    produce(sys.argv[1])


