*** Settings ***
Resource        atest_resource.robot
Suite Setup     Create Directory    ${OUTDIR}

*** Variables ***
${TESTPATH}     ${CURDIR}${/}..${/}..${/}..${/}utest${/}run.py

*** Test Cases ***
Unit Tests
    ${result} =    Run Process    @{INTERPRETER.interpreter}     ${TESTPATH}   --quiet
    ...    stdout=${STDOUT FILE}    stderr=STDOUT
    Log    ${result.stdout}
    Should Be Equal As Integers  ${result.rc}    0
    ...    Unit tests failed with RC ${result.rc}.    values=False
