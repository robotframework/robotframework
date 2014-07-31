*** Settings ***
Suite Setup     My Setup
Force Tags      regression
Default Tags    pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***
Python Library From A Zip File
    Check Test Case  Python Library From a Zip File
    Check Syslog Contains  Imported library 'ZipLib' with arguments [ ] (version <unknown>, class type, testcase scope, 1 keywords)

Java Library From A Jar File
    [Tags]  jybot
    Check Test Case  Java Library From a Jar File
    Check Syslog Contains  Imported library 'org.robotframework.JarLib' with arguments [ ] (version <unknown>, class type, testcase scope, 1 keywords)

*** Keywords ***
My Setup
    ${TESTLIBPATH} =  Join Path  ${CURDIR}${/}..${/}..  testresources/testlibs/
    Set Suite Variable  $TESTLIBPATH
    Run Tests  -P ${TESTLIBPATH}${/}ziplib.zip -P ${TESTLIBPATH}${/}JarLib.jar  test_libraries${/}library_import_from_archive.html

