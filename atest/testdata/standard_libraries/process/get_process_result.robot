*** Settings ***
Library           Process
Resource          process_resource.robot
Test Setup        Run Robot Process
Suite Teardown    Safe Remove File    ${TEMP FILE}

*** Variables ***
${TEMPFILE}       %{TEMPDIR}${/}get-process-result.txt

*** Test Cases ***
Get whole result object
    ${result} =    Get Process Result    robot
    Should Be Equal    ${result.rc}    ${2}
    Should Be Equal    ${result.stdout}    Robot
    Should Be Equal    ${result.stderr}    Framework
    Should Be Equal    ${result.stdout_path}    ${NONE}
    Should Be Equal    ${result.stderr_path}    ${TEMPFILE}

Get one result attribute
    ${rc} =    Get Process Result    rc=yes    handle=robot    stdout=FALSE
    Should Be Equal    ${rc}    ${2}

Get two result attribute
    ${rc}    ${stdout} =    Get Process Result    robot    1    2    false
    Should Be Equal    ${rc}    ${2}
    Should Be Equal    ${stdout}    Robot

Get all result attributes
    ${rc}    ${stdout}    ${stderr}    ${stdout_path}    ${stderr_path} =
    ...    Get Process Result    robot    stderr=yep    rc=x    stdout=${TRUE}
    ...    stderr_path=nämä    stdout_path=myös
    Should Be Equal    ${rc}    ${2}
    Should Be Equal    ${stdout}    Robot
    Should Be Equal    ${stderr}    Framework
    Should Be Equal    ${stdout_path}    ${NONE}
    Should Be Equal    ${stderr_path}    ${TEMPFILE}

Get same result multiple times
    ${result} =    Get Process Result    robot
    ${stdout} =    Get Process Result    robot    stdout=out
    ${stderr} =    Get Process Result    robot    stderr=err
    Should Be Equal    ${result.rc}    ${2}
    Should Be Equal    ${stdout}    Robot
    Should Be Equal    ${stderr}    Framework

Get result of active process
    Start Python Process    print('Robot Framework')
    Wait For Process
    ${result} =    Get Process Result
    ${stdout} =    Get Process Result    stdout=true
    Should Be Equal    ${result.rc}    ${0}
    Should Be Equal    ${result.stdout}    Robot Framework
    Should Be Equal    ${stdout}    Robot Framework

Getting results of unfinished processes is not supported
    [Documentation]    FAIL    Getting results of unfinished processes is not supported.
    Start Python Process    print('Robot Framework')
    Get Process Result

*** Keywords ***
Run Robot Process
    ${command} =    Catenate    SEPARATOR=;
    ...    import sys
    ...    sys.stdout.write('Robot')
    ...    sys.stderr.write('Framework')
    ...    sys.exit(2)
    Run Python Process   ${command}    alias=robot    stderr=${TEMPFILE}
