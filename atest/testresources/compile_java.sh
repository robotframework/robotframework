#!/bin/sh
if [ -z "$JYTHON_HOME" ]; then
    echo "Set JYTHON_HOME to compile."
    exit 1
fi
DIR="$( cd "$( dirname "$0" )" && pwd )"
OPTS="-cp $JYTHON_HOME/jython.jar -target 1.7 -source 1.7 $* -Xlint:unchecked"
javac $OPTS $DIR/testlibs/*.java
javac $OPTS $DIR/listeners/*.java
