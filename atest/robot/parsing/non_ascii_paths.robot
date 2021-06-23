*** Settings ***
Suite Setup       Create input data and run tests
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
    ${path} =    Normalize Path    %{TEMPDIR}/Työ/tyhjä.robot
    Syslog Should Contain    Data source '${path}' has no tests or tasks.

*** Keywords ***
Create input data and run tests
    Create input data
    Run Tests    --log ulog.html --report ureport.html    %{TEMPDIR}/testäö.robot %{TEMPDIR}/Työ

Create input data
    [Documentation]    Mercurial doesn't seem to handle non-ASCII file names too well.
    ...    Need to store files with ASCII names and rename them during execution.
    Copy Directory    ${BASEDIR}/Ty-ouml                     %{TEMPDIR}/Työ
    Move File         %{TEMPDIR}/Työ/tyhj-auml.robot         %{TEMPDIR}/Työ/tyhjä.robot
    Move File         %{TEMPDIR}/Työ/sect-test-sect.robot    %{TEMPDIR}/Työ/§test§.robot
    Copy File         ${BASEDIR}/test-auml-ouml.robot        %{TEMPDIR}/testäö.robot
