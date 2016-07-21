*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/variable_file_implemented_as_class.robot
Resource         atest_resource.robot

*** Test Cases ***

Python Class
    Check Test Case    ${TESTNAME}

Methods in Python Class Do Not Create Variables
    Check Test Case    ${TESTNAME}

Properties in Python Class
    Check Test Case    ${TESTNAME}

Dynamic Python Class
    Check Test Case    ${TESTNAME}

Java Class
    [Tags]    require-jython
    Check Test Case    ${TESTNAME}

Methods in Java Class Do Not Create Variables
    [Tags]    require-jython
    Check Test Case    ${TESTNAME}

Properties in Java Class
    [Tags]    require-jython
    Check Test Case    ${TESTNAME}

Dynamic Java Class
    [Tags]    require-jython
    Check Test Case    ${TESTNAME}

Instantiating Fails
    ${path} =    Normalize Path    ${DATADIR}/variables/InvalidClass.py
    Check Syslog Contains    Importing variable file '${path}' failed: Creating instance failed: TypeError:
