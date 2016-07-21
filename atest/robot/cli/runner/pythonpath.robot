*** Settings ***
Test Setup      Create Output Directory and Dymmy Library
Resource        cli_resource.robot

*** Variables ***
${DUMMY_LIB_TEST}  misc${/}dummy_lib_test.robot

*** Test Cases ***
Tests fail when library not in pythonpath
    Run Tests  ${EMPTY}  ${DUMMY_LIB_TEST}
    Should Be Equal  ${SUITE.status}  FAIL
    File Should Not Be Empty  ${STDERR FILE}

Pythonpath option
    Tests Should Pass Without Errors  --pythonpath ${CLI OUTDIR}  ${DUMMY_LIB_TEST}

Pythonpath option with multiple entries
    Tests Should Pass Without Errors  -P .:${CLI OUTDIR}${/}:%{TEMPDIR} -P ${CURDIR}  ${DUMMY_LIB_TEST}

Pythonpath option as glob pattern
    Tests Should Pass Without Errors  --pythonpath %{TEMPDIR}${/}c*i --escape star:STAR  ${DUMMY_LIB_TEST}

PYTHONPATH environment variable
    Set PYTHONPATH  ${CLI OUTDIR}    spam    eggs
    Tests Should Pass Without Errors  ${EMPTY}  ${DUMMY_LIB_TEST}
    [Teardown]  Reset PYTHONPATH

*** Keywords ***
Create Output Directory and Dymmy Library
    Create Output Directory
    Create File  ${CLI OUTDIR}/DummyLib.py  def dummykw():\n\tpass
