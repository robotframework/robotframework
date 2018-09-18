*** Settings ***
Test Setup        Create Output Directory and Dummy Library
Resource          cli_resource.robot

*** Variables ***
${TEST FILE}      misc/dummy_lib_test.robot

*** Test Cases ***
Tests fail when library not in pythonpath
    Run Tests    ${EMPTY}    ${TEST FILE}
    Should Be Equal    ${SUITE.status}    FAIL
    File Should Not Be Empty    ${STDERR FILE}

Pythonpath option
    Tests Should Pass Without Errors    --pythonpath ${CLI OUTDIR}    ${TEST FILE}

Pythonpath option with multiple entries
    Tests Should Pass Without Errors    -P .:${CLI OUTDIR}${/}:%{TEMPDIR} -P ${CURDIR}    ${TEST FILE}

Pythonpath option as glob pattern
    Tests Should Pass Without Errors    --pythonpath %{TEMPDIR}${/}c*i    ${TEST FILE}

PYTHONPATH environment variable
    Set PYTHONPATH    ${CLI OUTDIR}    spam    eggs
    Tests Should Pass Without Errors    ${EMPTY}    ${TEST FILE}
    [Teardown]    Reset PYTHONPATH

*** Keywords ***
Create Output Directory and Dummy Library
    Create Output Directory
    Create File    ${CLI OUTDIR}/DummyLib.py    def dummykw():\n\tpass
