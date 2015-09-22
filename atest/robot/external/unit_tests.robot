*** Settings ***
Suite Setup     Set Variables    unit
Force Tags      no-standalone
Resource        atest_resource.robot

*** Variables ***
${TESTPATH}     ${CURDIR}${/}..${/}..${/}..${/}utest${/}run_utests.py

*** Test Cases ***
Unit Tests
    ${result} =    Run Process    ${INTERPRETER.path}     ${TESTPATH}   --quiet
    ...    stderr=STDOUT
    Log    ${result.stdout}
    Should Be Equal As Integers  ${result.rc}    0
    ...    Unit tests failed with rc ${result.rc}.    values=False
