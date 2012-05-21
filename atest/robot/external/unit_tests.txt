*** Settings ***
Documentation   Robot unit tests
Suite Setup     Set Variables  unit
Force Tags      smoke  regression
Resource        atest_resource.txt

*** Variables ***
${TESTPATH}  ${CURDIR}${/}..${/}..${/}..${/}utest${/}run_utests.py

*** Test Cases ***
Unit Tests With Python
    [Tags]  pybot
    Run Unit Tests

Unit Tests With Jython
    [Tags]  jybot
    Run Unit Tests

*** Keywords ***
Run Unit Tests
    [Timeout]
    ${rc} =  Run And Return RC  ${INTERPRETER} ${TESTPATH} --quiet 1>${STDOUTFILE} 2> ${STDERRFILE}
    Get Stderr
    Get Stdout
    Should Be Equal As Integers  ${rc}  0  Unit tests failed with rc ${rc}.  False

