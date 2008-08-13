#!/bin/bash

ruby mylibrary.rb 1234 2> /dev/null &
sleep 1
pybot --variable PORT:1234 --log none --report none test/data/xmlrpc.html
../../tools/statuschecker/statuschecker.py output.xml
rebot output.xml
rc=$?
python test/running/XmlRpcServerHandler.py stop 1234
echo $rc tests failed

