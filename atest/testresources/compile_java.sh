#!/bin/sh
DIR="$( cd "$( dirname "$0" )" && pwd )"
javac -target 1.5 -source 1.5 $DIR/testlibs/*.java
if [ -n "$JYTHON_HOME" ]
then
    javac -cp $JYTHON_HOME/jython.jar -target 1.5 -source 1.5 $DIR/listeners/*.java
else
    echo set JYTHON_HOME to compile listeners
fi
