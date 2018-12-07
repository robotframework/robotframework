*** Settings ***
Suite Setup       Create input data and run tests
Suite Teardown    Revert input data
Resource          atest_resource.robot

*** Variables ***
${ROOT}           Testäö & Työ
${BASEDIR}        ${DATADIR}/parsing/non_ascii_paths

*** Test Cases ***
Non-ASCII characters in test case file name
    ${tc} =    Check Test Case    Non-ASCII Filename (€åäö§)
    Should Be Equal    ${tc.longname}    ${ROOT}.Testäö.Non-ASCII Filename (€åäö§)

Non-ASCII characters in test data directory name
    ${tc} =    Check Test Case    Non-ASCII Directory (€ÅÄÖ§)
    Should Be Equal    ${tc.longname}    ${ROOT}.Työ.§Test§.Non-ASCII Directory (€ÅÄÖ§)

Creating logs and reports should succeed
    [Documentation]    https://github.com/robotframework/robotframework/issues/530
    File Should Not Be Empty    ${OUTDIR}/ulog.html
    File Should Not Be Empty    ${OUTDIR}/ureport.html
    Stderr should be empty

Failures processing files are handled gracefully
    ${path} =    Normalize Path    ${BASEDIR}/Työ/tyhjä.robot
    Check syslog contains    Data source '${path}' has no tests or tasks.

*** Keywords ***
Create input data and run tests
    Create input data
    Run Tests    --log ulog.html --report ureport.html    parsing/non_ascii_paths/testäö.robot parsing/non_ascii_paths/Työ

Create input data
    [Documentation]    Mercurial doesn't seem to handle non-ASCII file names too well.
    ...    Need to store files with ASCII names and rename them during execution.
    Move Directory    ${BASEDIR}/Ty-ouml                     ${BASEDIR}/Työ
    Move File         ${BASEDIR}/Työ/tyhj-auml.robot         ${BASEDIR}/Työ/tyhjä.robot
    Move File         ${BASEDIR}/Työ/sect-test-sect.robot    ${BASEDIR}/Työ/§test§.robot
    Move File         ${BASEDIR}/test-auml-ouml.robot        ${BASEDIR}/testäö.robot

Revert input data
    [Documentation]    Revert ASCII -> non-ASCII conversion done by `Create input data`.
    Move File         ${BASEDIR}/Työ/§test§.robot   ${BASEDIR}/Työ/sect-test-sect.robot
    Move File         ${BASEDIR}/Työ/tyhjä.robot    ${BASEDIR}/Työ/tyhj-auml.robot
    Move Directory    ${BASEDIR}/Työ                ${BASEDIR}/Ty-ouml
    Move File         ${BASEDIR}/testäö.robot       ${BASEDIR}/test-auml-ouml.robot
