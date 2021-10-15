#!/usr/bin/env python

import fileinput
from os.path import join, dirname, abspath
import sys
import os

BASEDIR = dirname(abspath(__file__))
OUTPUT = join(BASEDIR, 'output.xml')

sys.path.insert(0, join(BASEDIR, '..', '..', '..', '..', 'src'))

import robot
from robot.conf.settings import RebotSettings
from robot.reporting.resultwriter import Results
from robot.reporting.jswriter import JsResultWriter, JsonWriter


def create(testdata, target, split_log=False):
    testdata = join(BASEDIR, testdata)
    output_name = target[0].lower() + target[1:-3] + 'Output'
    target = join(BASEDIR, target)
    run_robot(testdata)
    create_jsdata(target, split_log)
    inplace_replace_all(target, 'window.output', 'window.' + output_name)


def run_robot(testdata, output=OUTPUT):
    robot.run(testdata, log='NONE', report='NONE', output=output)


def create_jsdata(target, split_log, outxml=OUTPUT):
    result = Results(RebotSettings({'splitlog': split_log}), outxml).js_result
    config = {'logURL': 'log.html', 'reportURL': 'report.html', 'background': {'fail': 'DeepPink'}}
    with open(target, 'w') as output:
        JsResultWriter(output, start_block='', end_block='\n').write(result, config)
        writer = JsonWriter(output)
        for index, (keywords, strings) in enumerate(result.split_results):
            writer.write_json('window.outputKeywords%d = ' % index, keywords)
            writer.write_json('window.outputStrings%d = ' % index, strings)


def inplace_replace_all(file, search, replace):
    for line in fileinput.input(file, inplace=1):
        sys.stdout.write(line.replace(search, replace))


if __name__ == '__main__':
    create('Suite.robot', 'Suite.js')
    create('SetupsAndTeardowns.robot', 'SetupsAndTeardowns.js')
    create('Messages.robot', 'Messages.js')
    create('teardownFailure', 'TeardownFailure.js')
    create(join('teardownFailure', 'PassingFailing.robot'), 'PassingFailing.js')
    create('TestsAndKeywords.robot', 'TestsAndKeywords.js')
    create('.', 'allData.js')
    create('.', 'splitting.js', split_log=True)
    os.remove(OUTPUT)
