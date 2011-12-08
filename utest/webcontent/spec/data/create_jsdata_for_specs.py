#!/usr/bin/env python

import fileinput
from os.path import join, dirname, abspath
import sys
import os
from robot.result.datamodel import JSModelCreator
from robot.result.executionresult import ResultFromXml


BASEDIR = dirname(abspath(__file__))
OUTPUT = join(BASEDIR, 'output.xml')

sys.path.insert(0, join(BASEDIR, '..', '..', '..', '..', 'src'))

import robot
from robot.reporting.jswriter import SeparatingWriter, ScriptBlockWriter


def run_robot(testdata, loglevel='INFO'):
    robot.run(testdata, log='NONE', report='NONE',
              tagstatlink=['force:http://google.com:<kuukkeli&gt;',
                           'i*:http://%1/:Title of i%1'],
              tagdoc=['test:this_is_*my_bold*_test',
                      'IX:*Combined* & escaped <&lt; tag doc'],
              tagstatcombine=['fooANDi*:zap', 'i?:IX'],
              critical=[], noncritical=[], outputdir=BASEDIR, loglevel=loglevel)


def create_jsdata(outxml, target, split_log):
    result = ResultFromXml(outxml)
    visitor = JSModelCreator(split_log=split_log)
    result.visit(visitor)
    model = visitor.datamodel
    with open(target, 'w') as output:
        ScriptBlockWriter('\n').write_to(output, model, {'logURL': 'log.html',
                                                        'reportURL': 'report.html',
                                                        'background': {'fail': 'DeepPink'}})
        for index, (keywords, strings) in enumerate(model.split_results):
            writer = SeparatingWriter(output, '')
            writer.write_json('window.outputKeywords%d = ' % index, keywords)
            writer.write_json('window.outputStrings%d = ' % index, strings)

def replace_all(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)


def create(input, target, targetName, loglevel='INFO', split_log=False):
    input = join(BASEDIR, input)
    target = join(BASEDIR, target)
    run_robot(input, loglevel)
    create_jsdata(OUTPUT, target, split_log)
    replace_all(target, 'window.output', 'window.' + targetName)

if __name__ == '__main__':
    create('Suite.txt', 'Suite.js', 'suiteOutput')
    create('SetupsAndTeardowns.txt', 'SetupsAndTeardowns.js', 'setupsAndTeardownsOutput')
    create('Messages.txt', 'Messages.js', 'messagesOutput')
    create('teardownFailure', 'TeardownFailure.js', 'teardownFailureOutput')
    create(join('teardownFailure', 'PassingFailing.txt'), 'PassingFailing.js', 'passingFailingOutput')
    create('TestsAndKeywords.txt', 'TestsAndKeywords.js', 'testsAndKeywordsOutput')
    create('.', 'allData.js', 'allDataOutput')
    create('.', 'splitting.js', 'splittingOutput', split_log=True)
    os.remove(OUTPUT)
