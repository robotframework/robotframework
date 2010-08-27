#!/bin/sh
javac -target 1.5 -source 1.5 testlibs/*.java
javac -cp $JYTHON_HOME/jython.jar -target 1.5 -source 1.5 listeners/*.java