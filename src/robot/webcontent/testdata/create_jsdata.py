#!/usr/bin/env python

import os
import robot
from robot.result.jsparser import create_datamodel_from

BASEDIR = os.path.dirname(__file__)
TESTDATA = os.path.join(BASEDIR, 'dir.suite')
OUTPUT = os.path.join(BASEDIR, 'output.xml')
TARGET = os.path.join(BASEDIR, 'data.js')

if __name__ == '__main__':
    robot.run(TESTDATA, log='NONE', report='NONE',
              tagstatlink=['force:http://google.com:kuukkeli',
                           'i*:http://%1/:Title of i%1'],
              tagdoc=['test:this_is_*my_bold*_test', 'IX:*Combined* tag doc'],
              tagstatcombine=['fooANDi*:zap', 'i?:IX'],
              critical=['i?'], noncritical=['*kek*kone*'], outputdir=BASEDIR)
    model = create_datamodel_from(OUTPUT)
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(TARGET, 'w') as output:
        model.write_to(output)

