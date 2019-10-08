*** Settings ***
Resource          console_resource.robot

*** Variables ***
@{COMMAND}        @{INTERPRETER.runner}
...               --output           ${OUTPUT}
...               --report           NONE
...               --log              NONE
...               --pythonpath       ${CURDIR}${/}..${/}..${/}..${/}testresources${/}testlibs
...               ${DATADIR}${/}misc
${OUTPUT}         %{TEMPDIR}${/}piping.xml
${TARGET}         ${CURDIR}${/}piping.py

*** Test Cases ***
Pipe to command consuming all data
    Run with pipe and validate results    read_all
    Should Be Equal    ${STDOUT}    17 lines with 'FAIL' found!

Pipe to command consuming some data
    Run with pipe and validate results    read_some
    Should Be Equal    ${STDOUT}    Line with 'FAIL' found!

Pipe to command consuming no data
    Run with pipe and validate results    read_none
    Should Be Empty    ${STDOUT}

*** Keywords ***
Run with pipe and validate results
    [Arguments]    ${pipe style}
    ${command} =    Join Command Line    @{COMMAND}
    ${result} =    Run Process    ${command} | python ${TARGET} ${pipe style}
    ...    shell=true
    Log Many    RC: ${result.rc}    STDOUT:\n${result.stdout}    STDERR:\n${result.stderr}
    Should Be Equal    ${result.rc}    ${0}
    Process Output    ${OUTPUT}
    Check Test Case    Pass
    Check Test Case    Fail
    Set Test Variable    ${STDOUT}    ${result.stdout}
