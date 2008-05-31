#!/bin/bash

dir=$(dirname $0)
libdoc=$dir/../../tools/libdoc/libdoc.py

for lib in BuiltIn OperatingSystem Telnet Collections; do
    python $libdoc --output $dir/$lib.html $lib
done
