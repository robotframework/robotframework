#!/usr/bin/env python

import os
import robot
from robot.result.jsparser import create_datamodel_from

BASEDIR = os.path.dirname(__file__)
TESTDATA = os.path.join(BASEDIR, 'dir.suite')
OUTPUT = os.path.join(BASEDIR, 'output.xml')
TARGET = os.path.join(BASEDIR, 'data.js')

def run_robot(outputdirectory, testdata):
    robot.run(testdata, log='NONE', report='NONE',
              tagstatlink=['force:http://google.com:<kuukkeli&gt;',
                           'i*:http://%1/:Title of i%1'],
              tagdoc=['test:this_is_*my_bold*_test',
                      'IX:*Combined* & escaped <&lt; tag doc'],
              tagstatcombine=['fooANDi*:zap', 'i?:IX'],
              critical=['i?'], noncritical=['*kek*kone*'], outputdir=outputdirectory)


def create_jsdata(output_xml_file, target):
    model = create_datamodel_from(output_xml_file)
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(target, 'w') as output:
        model.write_to(output)

if __name__ == '__main__':
    run_robot(BASEDIR, TESTDATA)
    create_jsdata(OUTPUT, TARGET)

