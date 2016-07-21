*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  variables/list_as_scalar.robot
Resource        atest_resource.robot

*** Test Cases ***
Using List Variable As Scalar
    Check Test Case  ${TESTNAME}

List Variable As Scalar With Extended Syntax
    Check Test Case  ${TESTNAME}

Non-alphanumeric characters in name
    Check Test Case  ${TESTNAME}

Access and Modify List Variable With Keywords From Collections Library
    Check Test Case  ${TESTNAME}

Modifications To List Variables Live Between Test Cases
    Check Test Case  ${TESTNAME}
