#!/bin/bash
base=`dirname $0`
ROBOT_SYSLOG_FILE=$base/tmp/syslog.txt coverage run $base/src/robot/run.py -P $base/atest/testresources/testlibs -P $base/tmp -L debug -d $base/tmp "$@"
