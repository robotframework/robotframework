#!/bin/bash

cd $(dirname $0)/..

python python/examplelibrary.py 2> /dev/null &
sleep 1

pybot --log none --report none --output logs/output.xml $*

../../tools/statuschecker/statuschecker.py logs/output.xml
rebot --outputdir logs logs/output.xml

echo $? tests failed

