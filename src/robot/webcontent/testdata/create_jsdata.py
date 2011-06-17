import os
import robot
from robot.result.jsparser import create_datamodel_from

BASEDIR = os.path.dirname(__file__)
TESTDATA = os.path.join(BASEDIR, 'dir.suite')
OUTPUT = os.path.join(BASEDIR, 'output.xml')
TARGET = os.path.join(BASEDIR, 'data.js')

if __name__ == '__main__':
    robot.run(TESTDATA, tagstatlink=['force:http://google.com:kuukkeli'],
              tagdoc=['test:this_is_my_test'], tagstatcombine=['fooANDi*:zap'],
              critical=['i?'], noncritical=['*kekkone*'], outputdir=BASEDIR,
              log='NONE', report='NONE')
    model = create_datamodel_from(OUTPUT)
    model.set_settings({'logURL': 'log.html',
                        'reportURL': 'report.html',
                        'background': {'fail': 'DeepPink'}})
    with open(TARGET, 'w') as output:
        model.write_to(output)

