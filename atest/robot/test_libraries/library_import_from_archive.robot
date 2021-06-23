*** Settings ***
Suite Setup     My Setup
Resource        atest_resource.robot

*** Test Cases ***
Python Library From A Zip File
    Check Test Case  Python Library From a Zip File
    Syslog Should Contain  Imported library 'ZipLib' with arguments [ ] (version <unknown>, class type, TEST scope, 1 keywords)

Java Library From A Jar File
    [Tags]  require-jython
    Check Test Case  Java Library From a Jar File
    Syslog Should Contain  Imported library 'org.robotframework.JarLib' with arguments [ ] (version <unknown>, class type, TEST scope, 1 keywords)

*** Keywords ***
My Setup
    ${TESTLIBPATH} =  Normalize Path  ${CURDIR}/../../testresources/testlibs/
    Set Suite Variable  $TESTLIBPATH
    Run Tests  -P ${TESTLIBPATH}${/}ziplib.zip -P ${TESTLIBPATH}${/}JarLib.jar  test_libraries/library_import_from_archive.robot
