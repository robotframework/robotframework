#!/bin/bash

cd python
python examplelibrary.py 1234 2> /dev/null &
cd ..
sleep 1
pybot --variable PORT:1234 --log none --report none --output logs/output.xml test/xmlrpc.html
../../tools/statuschecker/statuschecker.py logs/output.xml
rebot --outputdir logs logs/output.xml
rc=$?
python test/XmlRpcServerHandler.py stop 1234
echo $rc tests failed

