#!/usr/bin/env python

from os.path import abspath, dirname, join
import sys

BASEDIR = dirname(abspath(__file__))
TESTDATA = join(BASEDIR, 'dir.suite')
OUTPUT = join(BASEDIR, 'output.xml')
TARGET = join(BASEDIR, 'data.js')

sys.path.insert(0, join(BASEDIR, '..', '..', '..'))

import robot
from robot.result.jsparser import create_datamodel_from


def run_robot(outputdirectory, testdata):
    robot.run(testdata, log='NONE', report='NONE',
              tagstatlink=['force:http://google.com:<kuukkeli&gt;',
                           'i*:http://%1/:Title of i%1'],
              tagdoc=['test:this_is_*my_bold*_test',
                      'IX:*Combined* & escaped <&lt; tag doc'],
              tagstatcombine=['fooANDi*:zap', 'i?:IX'],
              critical=['i?'], noncritical=['*kek*kone*'], outputdir=outputdirectory)


def create_jsdata(output_xml_file, target):
    model = create_datamodel_from(output_xml_file, log_path=join(BASEDIR,'..','log.html'))
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(target, 'w') as output:
        model.write_to(output)

if __name__ == '__main__':
    run_robot(BASEDIR, TESTDATA)
    create_jsdata(OUTPUT, TARGET)

