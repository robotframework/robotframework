ROOTDIR=`dirname $0`/..
LIBPATH=$ROOTDIR/lib
SRCPATH=$ROOTDIR/src
TESTDATA=$ROOTDIR/atest/vacalc
CP=$LIBPATH/robotframework-2.5.4.jar:$LIBPATH/swinglibrary-1.1.1.jar:$ROOTDIR/bin/
CLASSPATH=$CP java org.robotframework.RobotFramework -P $SRCPATH $* --outputdir $ROOTDIR/results $TESTDATA
