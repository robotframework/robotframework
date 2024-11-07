*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/non_string_variables.robot
Resource         atest_resource.robot
Variables        ${DATADIR}/variables/non_string_variables.py

*** Test Cases ***
Numbers
    Check Test Doc    ${TESTNAME}    I can has 42 and 3.14?

Bytes
    Check Test Doc    ${TESTNAME}    We has ${BYTES STR}!

Bytes concatenated with bytes yields bytes
    Check Test Doc    ${TESTNAME}    ${BYTES}${BYTEARRAY}${EMPTY}    # ${EMPTY} coerces value to a string

Collections
    Check Test Doc    ${TESTNAME}    ${LIST STR} ${DICT STR}

Misc
    Check Test Doc    ${TESTNAME}    True None ${MODULE STR}
