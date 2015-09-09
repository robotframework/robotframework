*** Settings ***
Suite Setup     Set Variables    unit
Force Tags      regression    no-standalone
Resource        atest_resource.robot

*** Variables ***
${TESTPATH}     ${CURDIR}${/}..${/}..${/}..${/}utest${/}run_utests.py

*** Test Cases ***
Unit Tests
    ${rc} =  Run And Return RC  ${INTERPRETER} ${TESTPATH} --quiet 1>${STDOUTFILE} 2> ${STDERRFILE}
    Get Stderr
    Get Stdout
    Should Be Equal As Integers  ${rc}  0  Unit tests failed with rc ${rc}.  False
