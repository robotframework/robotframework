#!/usr/bin/env python

from os.path import abspath, dirname, normpath, join
import os
import sys
import codecs

BASEDIR = dirname(abspath(__file__))
LOG = normpath(join(BASEDIR, '..', 'log.html'))
TESTDATA = join(BASEDIR, 'dir.suite')
OUTPUT = join(BASEDIR, 'output.xml')
TARGET = join(BASEDIR, 'data.js')
SRC = normpath(join(BASEDIR, '..', '..', '..'))

sys.path.insert(0, SRC)

import robot
from robot.conf.settings import RebotSettings
from robot.reporting.resultwriter import Results
from robot.reporting.jswriter import JsResultWriter
from robot.utils import utf8open

def run_robot(testdata, outxml):
    robot.run(testdata, loglevel='DEBUG', log='NONE', report='NONE', output=outxml)


def create_jsdata(outxml, target):
    settings = RebotSettings({
        'critical': ['i?'],
        'noncritical': ['*kek*kone*'],
        'tagstatlink': ['force:http://google.com:<kuukkeli&gt;',
                        'i*:http://%1/:Title of i%1'],
        'tagdoc': ['test:this_is_*my_bold*_test',
                   'IX:*Combined* & escaped <&lt; tag doc'],
        'tagstatcombine': ['fooANDi*:No Match', 'i?:IX']
    })
    result = Results(outxml, settings).js_result
    config = {'logURL': 'log.html',
              'reportURL': 'report.html',
              'background': {'fail': 'DeepPink'}}
    with utf8open(target, 'w') as output:
        writer = JsResultWriter(output, start_block='', end_block='')
        writer.write(result, config)
    print 'Log:    ', normpath(join(BASEDIR, '..', 'log.html'))
    print 'Report: ', normpath(join(BASEDIR, '..', 'report.html'))


if __name__ == '__main__':
    run_robot(TESTDATA, OUTPUT)
    create_jsdata(OUTPUT, TARGET)
    os.remove(OUTPUT)
