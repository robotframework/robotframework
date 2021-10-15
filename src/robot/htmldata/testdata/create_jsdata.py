#!/usr/bin/env python

from __future__ import print_function

from os.path import abspath, dirname, normpath, join
import os
import sys

BASEDIR = dirname(abspath(__file__))
LOG = normpath(join(BASEDIR, '..', 'log.html'))
TESTDATA = join(BASEDIR, 'dir.suite')
OUTPUT = join(BASEDIR, 'output.xml')
TARGET = join(BASEDIR, 'data.js')
SRC = normpath(join(BASEDIR, '..', '..', '..'))

sys.path.insert(0, SRC)

from robot import run
from robot.conf.settings import RebotSettings
from robot.reporting.resultwriter import Results
from robot.reporting.jswriter import JsResultWriter
from robot.utils import file_writer


def run_robot(testdata, outxml):
    run(testdata, loglevel='DEBUG', output=outxml, log=None, report=None)


def create_jsdata(outxml, target):
    settings = RebotSettings({
        'name': '<Suite.Name>',
        'critical': ['i?'],
        'noncritical': ['*kek*kone*'],
        'tagstatlink': ['force:http://google.com:<kuukkeli&gt;',
                        'i*:http://%1/?foo=bar&zap=%1:Title of i%1',
                        '?1:http://%1/<&>:Title',
                        '</script>:<url>:<title>'],
        'tagdoc': ['test:this_is_*my_bold*_test',
                   'IX:*Combined* and escaped <&lt; tag doc',
                   'i*:Me, myself, and I.',
                   '</script>:<doc>'],
        'tagstatcombine': ['fooANDi*:No Match',
                           'long1ORcollections',
                           'i?:IX',
                           '<*>:<any>']
    })
    result = Results(settings, outxml).js_result
    config = {'logURL': 'log.html',
              'title': 'This is a long long title. A very long title indeed. '
                       'And it even contains some stuff to <esc&ape>. '
                       'Yet it should still look good.',
              'minLevel': 'DEBUG',
              'defaultLevel': 'DEBUG',
              'reportURL': 'report.html',
              'background': {'fail': 'DeepPink'}}
    with file_writer(target) as output:
        writer = JsResultWriter(output, start_block='', end_block='')
        writer.write(result, config)
    print('Log:    ', normpath(join(BASEDIR, '..', 'rebot', 'log.html')))
    print('Report: ', normpath(join(BASEDIR, '..', 'rebot', 'report.html')))


if __name__ == '__main__':
    run_robot(TESTDATA, OUTPUT)
    create_jsdata(OUTPUT, TARGET)
    os.remove(OUTPUT)
