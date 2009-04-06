#!/bin/bash
basedir=$PWD/test
pybot --loglevel DEBUG --log none --report none --outputdir $basedir $basedir/example.html
python $basedir/../statuschecker.py $basedir/output.xml
rebot $basedir/output.xml


