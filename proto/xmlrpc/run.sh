#!/bin/bash

cd ruby
ruby examplelibrary.rb 1234 2> /dev/null &
cd ..
sleep 1
pybot --variable PORT:1234 --log none --report none test/xmlrpc.html
../../tools/statuschecker/statuschecker.py output.xml
rebot output.xml
rc=$?
python test/XmlRpcServerHandler.py stop 1234
echo $rc tests failed

