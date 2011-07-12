#!/usr/bin/env python

import fileinput
from os.path import join, dirname, abspath
import sys

BASEDIR = dirname(abspath(__file__))
print BASEDIR

sys.path.insert(0, join(BASEDIR, '..', '..', '..', '..', 'src'))
print sys.path[0]

import robot
from robot.result.jsparser import create_datamodel_from


def run_robot(testdata, loglevel='INFO'):
    robot.run(testdata, log='NONE', report='NONE',
              tagstatlink=['force:http://google.com:<kuukkeli&gt;',
                           'i*:http://%1/:Title of i%1'],
              tagdoc=['test:this_is_*my_bold*_test',
                      'IX:*Combined* & escaped <&lt; tag doc'],
              tagstatcombine=['fooANDi*:zap', 'i?:IX'],
              critical=[], noncritical=[], outputdir=BASEDIR, loglevel=loglevel)


def create_jsdata(output_xml_file, target):
    model = create_datamodel_from(output_xml_file)
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(target, 'w') as output:
        model.write_to(output)

def replace_all(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)


def create(input, target, targetName, loglevel='INFO'):
    input = join(BASEDIR, input)
    target = join(BASEDIR, target)
    outxml = join(BASEDIR, 'output.xml')
    run_robot(input, loglevel)
    create_jsdata(outxml, target)
    replace_all(target, 'window.output', 'window.' + targetName)

if __name__ == '__main__':
    create('Suite.txt', 'Suite.js', 'suiteOutput')
    create('SetupsAndTeardowns.txt', 'SetupsAndTeardowns.js', 'setupsAndTeardownsOutput')
    create('Messages.txt', 'Messages.js', 'messagesOutput')
    create('teardownFailure', 'TeardownFailure.js', 'teardownFailureOutput')
    create(join('teardownFailure', 'PassingFailing.txt'), 'PassingFailing.js', 'passingFailingOutput')
    create('TestsAndKeywords.txt', 'TestsAndKeywords.js', 'testsAndKeywordsOutput')
    create('.', 'allData.js', 'allDataOutput')

