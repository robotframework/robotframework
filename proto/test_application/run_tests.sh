#!/bin/bash
export CLASSPATH=lib:lib/swinglibrary-0.12-SNAPSHOT.jar
jybot --pythonpath lib/ --loglevel debug --outputdir result $*

