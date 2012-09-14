*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/non_string_variables.txt
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt
Variables        ../../testdata/variables/non_string_variables.py    ${INTERPRETER}

*** Test Cases ***

Numbers
    Check Test Doc    ${TESTNAME}    I can has 42 and 3.14?

Byte string
    Check Test Doc    ${TESTNAME}    We has ${BYTE STRING STR}!

Collections
    Check Test Doc    ${TESTNAME}    ${LIST STR} ${DICT STR}

Misc
    Check Test Doc    ${TESTNAME}    True None ${MODULE STR}
