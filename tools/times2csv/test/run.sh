#!/bin/sh
testdir=`dirname $0`
rm -f $testdir/output.*
export PYTHONPATH=$testdir/../../../src
python -m robot.run -l none -r none -d $testdir $testdir/test.txt
python $testdir/../times2csv.py $testdir/output.xml
echo "------------------------------ results ------------------------------"
cat $testdir/output.csv
echo "-------------------------------- end --------------------------------"
echo "Verify above results manually. Or enhance this script to automate it."
