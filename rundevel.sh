#!/bin/bash
ROBOT_SYSLOG_FILE=tmp/syslog.txt python src/robot/runner.py -P atest/testresources/testlibs -P tmp -L debug -d tmp $*
