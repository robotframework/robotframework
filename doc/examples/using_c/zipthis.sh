#!/bin/bash

dirname=robotframework-c-example
zipname=$dirname-$(date +%Y%m%d).zip
files="README.txt login.c LoginLibrary.py LoginTests.tsv Makefile"

rm -rf $dirname $zipname
mkdir $dirname
echo Copying...
for file in $files; do
    cp -v $file $dirname
done
echo Zipping...
zip -r $zipname $dirname
rm -rf $dirname
echo Created $zipname
