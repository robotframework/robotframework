set ROOTDIR=%~dp0..
set LIBPATH=%ROOTDIR%\lib
set SRCPATH=%ROOTDIR%\src
set TESTDATA=%ROOTDIR%\atest\vacalc
set CLASSPATH=%LIBPATH%\robotframework-2.5.4.1.jar;%LIBPATH%\swinglibrary-1.1.1.jar;%ROOTDIR%\bin
java org.robotframework.RobotFramework -P %SRCPATH% -P %ROOTDIR%\atest\libraries %* --outputdir %ROOTDIR%\results --critical regression %TESTDATA%


