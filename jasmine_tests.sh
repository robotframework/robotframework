#!/bin/bash
jasmine_reporters_git=https://github.com/larrymyers/jasmine-reporters.git
reporter_version=0.2.1

base=`dirname $0`
jasmine_reporters_path=$base/ext-lib/jasmine-reporters
jasmine_results_path=$base/jasmine-results
export PATH=$PATH:/usr/local/bin
if [ ! -d $jasmine_reporters_path ]
    then
        echo Cloning Jasmine-Reporters
        (cd $base/ext-lib ; git clone $jasmine_reporters_git ; cd jasmine-reporters ; git checkout --quiet $reporter_version)
        echo Jasmine-Reporters $reporter_version cloned 
fi
if [ -d $jasmine_results_path ]
    then
        echo Removing old test results
        rm -rf $jasmine_results_path
fi
echo Creating jasmine results path $jasmine_results_path
mkdir $jasmine_results_path
(cd $base ; java -cp ext-lib/jasmine-reporters/ext/js.jar:ext-lib/jasmine-reporters/ext/jline.jar org.mozilla.javascript.tools.shell.Main -opt -1 envjs.bootstrap.js utest/webcontent/SpecRunner.html)
