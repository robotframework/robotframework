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

Instantiating Fails
    ${path} =    Normalize Path    ${DATADIR}/variables/InvalidClass.py
    Error In File    -1    variables/variable_file_implemented_as_class.robot    4
    ...    Processing variable file '${path}' failed:
    ...    Importing variable file '${path}' failed:
    ...    Variable file 'InvalidClass' expected 4 arguments, got 0.
