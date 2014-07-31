*** Settings ***
Documentation   Verify that even if __init__ file fails, the documentation from that file is available in the suite
Suite Setup     Run Tests  ${EMPTY}  parsing/failing_init/
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***
Failing Init
    Should Be Equal  ${SUITE.doc}  This should exist
    ${path} =  Join Path  ${CURDIR}  ../../testdata  parsing/failing_init/
    Check Log Message  ${ERRORS.msgs[0]}  Test suite init file in '${path}' contains a test case table which is not allowed.  ERROR
    Check Test Case  Fail Init

