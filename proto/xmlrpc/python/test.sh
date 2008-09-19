#!/bin/bash

base=$(dirname $0)
cd $base/..

python python/examplelibrary.py 2> /dev/null &
sleep 1
pybot --log none --report none --output logs/output.xml test/remote_library.html
../../tools/statuschecker/statuschecker.py logs/output.xml
rebot --outputdir logs logs/output.xml
rc=$?
python test/XmlRpcServerHandler.py stop
echo $rc tests failed

