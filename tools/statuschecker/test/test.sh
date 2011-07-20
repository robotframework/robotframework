#!/bin/bash
testdir=`dirname $0`
pybot --loglevel DEBUG --log none --report none --outputdir $testdir $testdir/example.txt
python $testdir/../statuschecker.py $testdir/output.xml
rebot $testdir/output.xml
echo "$? tests failed, 5 should have failed."
echo "Check that tests starting with 'FAILURE:' have failed and others passed."


