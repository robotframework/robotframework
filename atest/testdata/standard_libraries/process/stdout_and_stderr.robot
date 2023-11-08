*** Settings ***
Resource          process_resource.robot
Test Teardown     Safe Remove File    ${STDOUT}    ${STDERR}

*** Test Cases ***
Default stdout and stderr
    ${result} =    Run Stdout Stderr Process
    Result Should Equal    ${result}    stdout    stderr

Custom stdout
    ${result} =    Run Stdout Stderr Process    stdout=${STDOUT}
    Result Should Equal    ${result}    stdout    stderr    stdout_path=${STDOUT}

Custom stdout as `pathlib.Path`
    ${result} =    Run Stdout Stderr Process    stdout=${{pathlib.Path($STDOUT)}}
    Result Should Equal    ${result}    stdout    stderr    stdout_path=${STDOUT}

Redirecting stdout to DEVNULL
    ${result} =    Run Stdout Stderr Process    stdout=DEVNULL
    Should Not Exist      ${EXECDIR}/DEVNULL
    Should Be Empty       ${result.stdout}
    Should Contain Any    ${result.stdout_path}    /dev/null    nul
    Should Be Equal       ${result.stderr}    stderr

Custom stderr
    ${result} =    Run Stdout Stderr Process    stderr=${STDERR}
    Result Should Equal    ${result}    stdout    stderr    stderr_path=${STDERR}

Custom stderr as `pathlib.Path`
    ${result} =    Run Stdout Stderr Process    stderr=${{pathlib.Path($STDERR)}}
    Result Should Equal    ${result}    stdout    stderr    stderr_path=${STDERR}

Custom stdout and stderr
    ${result} =    Run Stdout Stderr Process    stdout=${STDOUT}    stderr=${STDERR}
    Result Should Equal    ${result}    stdout    stderr    stdout_path=${STDOUT}    stderr_path=${STDERR}

Custom stdout and stderr to same file
    ${result} =    Run Stdout Stderr Process    stdout=${STDOUT}    stderr=${STDOUT}
    Result Should Match    ${result}    std???std???    std???std???
    ...    stdout_path=${STDOUT}    stderr_path=${STDOUT}

Redirecting stderr to stdout
    ${result} =    Run Stdout Stderr Process    stderr=STDOUT
    Result Should Match    ${result}    std???std???

Redirecting stderr to custom stdout
    ${result} =    Run Stdout Stderr Process    stdout=${STDOUT}    stderr=STDOUT
    Result Should Match    ${result}    std???std???    std???std???
    ...    stdout_path=${STDOUT}    stderr_path=${STDOUT}

Redirecting stderr to DEVNULL
    ${result} =    Run Stdout Stderr Process    stderr=DEVNULL
    Should Not Exist      ${EXECDIR}/DEVNULL
    Should Be Equal       ${result.stdout}    stdout
    Should Be Empty       ${result.stderr}
    Should Contain Any    ${result.stderr_path}    /dev/null    nul

Redirecting stdout and stderr to DEVNULL
    ${result} =    Run Stdout Stderr Process    stdout=DEVNULL    stderr=DEVNULL
    Should Not Exist      ${EXECDIR}/DEVNULL
    Should Be Empty       ${result.stdout}
    Should Contain Any    ${result.stdout_path}    /dev/null    nul
    Should Be Empty       ${result.stderr}
    Should Contain Any    ${result.stderr_path}    /dev/null    nul

Redirecting stdout to DEVNULL and stderr to STDOUT
    ${result} =    Run Stdout Stderr Process    stdout=DEVNULL    stderr=STDOUT
    Should Not Exist      ${EXECDIR}/DEVNULL
    Should Be Empty       ${result.stdout}
    Should Contain Any    ${result.stdout_path}    /dev/null    nul
    Should Be Empty       ${result.stderr}
    Should Contain Any    ${result.stderr_path}    /dev/null    nul

Custom streams are written under cwd when relative
    [Setup]    Create Directory    ${CWD}
    ${result} =    Run Stdout Stderr Process    cwd=${CWD}    stdout=stdout.txt    stderr=stderr.txt
    Result Should Equal    ${result}    stdout    stderr    stdout_path=${CWD}/stdout.txt    stderr_path=${CWD}/stderr.txt
    [Teardown]    Safe Remove Directory    ${CWD}

Cwd does not affect absolute custom streams
    [Setup]    Create Directory    ${CWD}
    ${result} =    Run Stdout Stderr Process    cwd=${CWD}    stdout=${STDOUT}    stderr=${STDERR}
    Result Should Equal    ${result}    stdout    stderr    stdout_path=${STDOUT}    stderr_path=${STDERR}
    [Teardown]    Safe Remove Directory    ${CWD}

Lot of output to custom stream
    [Tags]    performance
    ${result}=    Run Process    python -c "for i in range(100000):\tprint('a'*99)"    shell=True    stdout=${STDOUT}
    Should Be Equal    ${result.rc}    ${0}
    Length Should Be    ${result.stdout}    9999999
    File Should Not Be Empty    ${STDOUT}

Lot of output to DEVNULL
    [Tags]    performance
    ${result}=    Run Process    python -c "for i in range(100000):\tprint('a'*99)"    shell=True    stdout=DEVNULL
    Should Be Empty    ${result.stdout}
    Should Be Empty    ${result.stderr}
    Should Be Equal    ${result.rc}    ${0}

Run multiple times
    [Tags]    performance
    FOR    ${i}    IN RANGE    100
       Run And Test Once    ${i}
    END

Run multiple times using custom streams
    [Tags]    performance
    FOR    ${i}    IN RANGE    100
       Run And Test Once    ${i}    ${STDOUT}    ${STDERR}
    END

Read standard streams when they are already closed externally
    Some Process    stderr=${NONE}
    ${stdout} =    Stop Some Process    message=42
    Should Be Equal    ${stdout}    42
    ${process} =    Get Process Object
    Run Keyword If    not ${process.stdout.closed}
    ...    Call Method    ${process.stdout}    close
    Run Keyword If    not ${process.stderr.closed}
    ...    Call Method    ${process.stderr}    close
    ${result} =    Wait For Process
    Should Be Empty    ${result.stdout}${result.stderr}

*** Keywords ***
Run Stdout Stderr Process
    [Arguments]    ${stdout}=${NONE}    ${stderr}=${NONE}    ${cwd}=${NONE}
    ...    ${stdout_content}=stdout    ${stderr_content}=stderr
    ${code} =    Catenate    SEPARATOR=;
    ...    import sys
    ...    sys.stdout.write('${stdout_content}')
    ...    sys.stderr.write('${stderr_content}')
    ${result} =    Run Process    python    -c    ${code}
    ...    stdout=${stdout}    stderr=${stderr}    cwd=${cwd}
    RETURN    ${result}

Run And Test Once
    [Arguments]    ${content}    ${stdout}=${NONE}    ${stderr}=${NONE}
    ${result} =    Run Stdout Stderr Process    stdout=${stdout}    stderr=${stderr}
    ...    stdout_content=out-${content}    stderr_content=err-${content}
    Should Be Equal   ${result.stdout}    out-${content}
    Should Be Equal   ${result.stderr}    err-${content}
