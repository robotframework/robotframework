#!/bin/sh
testdir=`dirname $0`
rm -f $testdir/output.*
pybot --log none --report none --outputdir $testdir $testdir/test.txt
python $testdir/../times2csv.py $testdir/output.xml
echo "------------------------------ results ------------------------------"
cat $testdir/output.csv
echo "-------------------------------- end --------------------------------"
echo "Verify above results manually. Or enhance this script to automate it."
