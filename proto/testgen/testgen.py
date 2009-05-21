#!/usr/bin/env python

"""A tool for creating data driven test case for Robot Framework

Usage:  testgen.py variablefile template output

This script reads the variable and template files and generates a test suite
which has all test cases found in the template multiplied with all the rows of
the variable file. Suite settings, variables and user keywords from the template
file are serialized as is.

Currently, the input files must be in tsv (tab separated values) format.  Also
the output file is written in tsv. The variables file must have a format
demonstrated in the example below, e.g. header row, followed by a row with the
names of the variables, and on the subsequent rows the values for the
variables.

Options:
 -h -? --help             Print this usage instruction.

Example:
<<template.tsv>>
* Settings *
Documentation   Example data driven suite
* Test Cases *
Example Test    Keyword ${arg1} ${arg2}
* User Keywords *
Keyword [Arguments] ${val1} ${val2}
    Log Many    ${val1} ${val2} 

<<variables.tsv>>
* Variables *
${arg1} ${arg2}
value1  value2
value11 value22

Given above files, command 
python testgen.py variables.tsv template.tsv output.tsv
produces following test suite:

<<output.tsv>>
* Settings *
Documentation   Example data driven suite
* Test Cases *
Example Test 1  Keyword value1  value2  
Example Test 2  Keyword value11 value22
* User Keywords *
Keyword [Arguments] ${val1} ${val2}
    Log Many    ${val1} ${val2} 
"""
import sys
import os
import csv

from robot.parsing.model import FileSuite
from robot.parsing.tsvreader import TsvReader
from robot.errors import DataError, Information
from robot import utils


class TestGeneratingSuite(FileSuite):

    def serialize(self, variables, serializer):
        self._serialize_settings(serializer)
        self._serialize_variables(serializer)
        self._serialize_tests(variables, serializer)
        self._serialize_keywords(serializer)

    def _serialize_settings(self, serializer):
        serializer.start_settings()
        if self.doc:
            serializer.setting('Documentation', self.doc)
        for name, value in self.metadata.items():
            serializer.setting('Meta: %s' % name, [value])
        for name in ['Default Tags', 'Force Tags', 'Suite Setup',
                     'Suite Teardown', 'Test Setup', 'Test Teardown',
                     ]:
            value = self._get_setting(self, name)
            if value:
                serializer.setting(name, value)
        for imp in self.imports:
            serializer.setting(imp.name, imp._item.value)
        serializer.end_settings()

    def _serialize_variables(self, serializer):
        serializer.start_variables()
        for var in self.variables:
            serializer.variable(var.name, var.value)
        serializer.end_variables()
                
    def _serialize_tests(self, variables, serializer):
        serializer.start_testcases()
        for test in self.tests:
            orig_name = test.name
            for index, vars in enumerate(variables):
                test.name = '%s %d' % (orig_name, (index+1))
                serializer.start_testcase(test)
                if test.doc:
                    serializer.setting('Documentation', [test.doc])
                for name in ['Setup', 'Tags', 'Timeout']:
                    value = self._get_setting(test, name)
                    if value is not None:
                        serializer.setting(name, value)
                for kw in test.keywords:
                    data = self._replace_variables(vars, [kw.name] + kw.args)
                    serializer.keyword(data)
                if test.teardown is not None:
                    serializer.setting('Teardown', test.teardown)
                serializer.end_testcase()
        serializer.end_testcases()

    def _serialize_keywords(self, serializer):
        serializer.start_keywords()
        for uk in self.user_keywords:
            serializer.start_keyword(uk)
            args = self._format_args(uk.args, uk.defaults, uk.varargs)
            if args:
                serializer.setting('Arguments', args)
            if uk.doc:
                serializer.setting('Documentation', uk.doc)
            if uk.timeout is not None:
                serializer.setting('Timeout', uk.timeout)
            for kw in uk.keywords:
                serializer.keyword([kw.name] + kw.args)
            if uk.return_value:
                serializer.setting('Return Value', uk.return_value)
        serializer.end_keywords()

    def _replace_variables(self, variables, data):
        replaced = []
        for elem in data:
            for key in variables:
                if key in elem:
                    elem = elem.replace(key, variables[key])
            replaced.append(elem)
        return replaced

    def _get_setting(self, item, name):
        return getattr(item, name.lower().replace(' ', '_'))

    def _format_args(self, args, defaults, varargs):
        parsed = []
        if args:
            parsed.extend(list(args))
        if defaults:
            for i, value in enumerate(defaults):
                index = len(args) - len(defaults) + i
                parsed[index] = parsed[index] + '=' + value            
        if varargs:
            parsed.append(varargs)
        return parsed


class VariableIterator(object):

    def __init__(self, varfile):
        self._variable_mapping = {}
        self._variables = []
        TsvReader().read(varfile, self)

    def __iter__(self):
        while self._variables:
            data = self._variables.pop(0)
            values = {}
            for key in self._variable_mapping:
                values[key] = data[self._variable_mapping[key]]
            yield values
    
    def start_table(self, name):
        return name.lower().strip() == 'variables' 

    def add_row(self, row):
        if not self._variable_mapping:
            for pos in range(len(row)):
                self._variable_mapping[row[pos]] = pos
        else:
            self._variables.append(row)


class AbstractFileWriter(object):
    
    def __init__(self, path, cols):
        self._output = open(path, 'wb')
        self._cols = cols
        self._tc_name = None
        self._uk_name = None
    
    def start_settings(self):
        self._write_header_row(['Setting', 'Value'])
        
    def end_settings(self):
        self._write_empty_row()
        
    def start_variables(self):
        self._write_header_row(['Variable', 'Value'])
        
    def end_variables(self):
        self._write_empty_row()

    def start_testcases(self):
        self._write_header_row(['Test Case', 'Action', 'Argument'])
        
    def end_testcases(self):
        self._write_empty_row()

    def start_testcase(self, testcase):
        self._tc_name = testcase.name
        
    def end_testcase(self):
        if self._tc_name:
            self._write_normal_row([self._tc_name])
        self._tc_name = None
        self._write_empty_row()

    def start_keywords(self):
        self._write_header_row(['Keyword', 'Action', 'Argument'])
        
    def end_keywords(self):
        self._write_empty_row()
        self._output.close()

    def start_keyword(self, userkeyword):
        self._uk_name = userkeyword.name
        
    def end_keyword(self):
        if self._uk_name:
            self._write_normal_row([self._uk_name])
        self._uk_name = None
        self._write_empty_row()
        
    def setting(self, name, value):
        if self._tc_name is None and self._uk_name is None:
            self._write_normal_row([name] + value)
        else: # TC and UK settings
            row = [self._get_tc_or_uk_name(), '[%s]' % name] + value
            self._write_normal_row(row, indent=1)
        
    def variable(self, name, value):
        self._write_normal_row([name] + value)

    def keyword(self, keyword):
        name = self._get_tc_or_uk_name()
        # TODO: When adding support for PARALLEL, FOR, etc. need to use 
        # different indent when inside indented block
        self._write_normal_row([name] + keyword, indent=1)
        
    def _write_header_row(self, row):
        row += [row[-1]] * (self._cols - len(row))
        self._write_header_row_impl(row)
        
    def _write_normal_row(self, row, indent=0):
        firstrow = True
        while True:
            if firstrow:
                current = row[:self._cols]
                row = row[self._cols:]
                firstrow = False
            else:
                current = ['']*indent + ['...'] + row[:self._cols-indent-1]
                row = row[self._cols-indent-1:]
            self._escape_empty_trailing_cells(current)
            current += [''] * (self._cols - len(current))
            self._write_normal_row_impl(current)
            if not row:
                break

    def _write_empty_row(self):
        self._write_normal_row([])

    def _escape_empty_trailing_cells(self, row):
        if len(row) > 0 and row[-1] == '':
            row[-1] = '\\'

    def _get_title(self, path):
        dire, base = os.path.split(path)
        if base.lower() == '__init__.html':
            path = dire
        return utils.printable_name_from_path(path)

    def _write_header_row_impl(self, row):
        raise NotImplementedError

    def _write_normal_row_impl(self, row):
        raise NotImplementedError
    

class TsvFileWriter(AbstractFileWriter):
    
    def __init__(self, path):
        AbstractFileWriter.__init__(self, path, 8)
        self._writer = csv.writer(self._output, dialect='excel-tab')

    def _write_header_row_impl(self, row):
        self._writer.writerow(['*%s*' % cell for cell in row])
        
    def _write_normal_row_impl(self, row):
        self._writer.writerow([cell.encode('UTF-8') for cell in row])

    def _get_tc_or_uk_name(self):
        if self._tc_name:
            name = self._tc_name
            self._tc_name = ''
        elif self._uk_name:
            name = self._uk_name
            self._uk_name = ''
        else:
            name = ''
        return name


def generate_suite(cliargs):
    opts, (varfile, templatefile, outfile) = _process_args(cliargs)
    suite = TestGeneratingSuite(templatefile)
    vars = VariableIterator(open(varfile))
    if not outfile.endswith('tsv'):
        outfile = outfile + '.tsv'
    suite.serialize(vars, TsvFileWriter(outfile))

def _process_args(cliargs):
    ap = utils.ArgumentParser(__doc__, arg_limits=(3, sys.maxint))
    try:
        opts, paths = ap.parse_args(cliargs, help='help', check_args=True)
    except Information, msg:
        exit(msg=str(msg))
    except DataError, err:
        exit(error=str(err))
    return opts, paths

def exit(rc=0, error=None, msg=None):
    if error:
        print error, "\n\nUse '--help' option to get usage information."
        if rc == 0:
            rc = 255
    if msg:
        print msg
        rc = 1
    sys.exit(rc)


if __name__ == '__main__':
    generate_suite(sys.argv[1:])
