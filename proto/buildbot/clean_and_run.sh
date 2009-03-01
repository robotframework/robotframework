#!/bin/bash
name=`basename $0`
basedir=`echo $PWD/$0 | sed s/$name//`
rm -rf $basedir/results

echo $0
../../TESTENV/bin/python $basedir/run_atests.py $*

