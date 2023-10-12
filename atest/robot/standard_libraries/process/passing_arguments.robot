*** Settings ***
Suite Setup      Run Tests    --loglevel DEBUG    standard_libraries/process/passing_arguments.robot
Test Template    Python script should be run and arguments logged
Resource         atest_resource.robot

*** Test Cases ***
Command and arguments in system
    "my stdout" "my stderr"

Command and arguments in shell as separate arguments
    "my stdout"

Command and arguments in shell as single argument
    my args

Non-ASCII arguments separately
    stdout:hyvää stderr:päivää encoding:UTF-8    script=encoding.py

Non-ASCII arguments separately when using shell
    stdout:hyvää stderr:päivää encoding:UTF-8    script=encoding.py

Non-ASCII arguments in as string when using shell
    stdout:hyvää stderr:päivää encoding:UTF-8    script=encoding.py

Arguments are converted to strings automatically
    1 2 3

Escaping equal sign
    name\=value    index=0
    shell\=False   index=2

Unsupported kwargs cause error
    [Template]    NONE
    Check Test Case    ${TESTNAME}

Log process config
    [Template]    NONE
    ${tc} =   Arguments should be logged    python -c pass
    ${config} =    Catenate    SEPARATOR=\n
    ...    cwd:${SPACE*5}%{TEMPDIR}
    ...    shell:${SPACE*3}True
    ...    stdout:${SPACE*2}%{TEMPDIR}${/}stdout
    ...    stderr:${SPACE*2}PIPE
    ...    stdin:${SPACE*3}None
    ...    alias:${SPACE*3}äliäs
    ...    env:${SPACE*5}None
    Check Log Message    ${tc.kws[0].msgs[1]}    Process configuration:\n${config}    level=DEBUG
    ${cwd} =    Normalize Path    ${DATADIR}/standard_libraries/process
    ${config} =    Catenate    SEPARATOR=\n
    ...    cwd:${SPACE*5}${cwd}
    ...    shell:${SPACE*3}False
    ...    stdout:${SPACE*2}PIPE
    ...    stderr:${SPACE*2}STDOUT
    ...    stdin:${SPACE*3}PIPE
    ...    alias:${SPACE*3}None
    ...    env:${SPACE*5}None
    Check Log Message    ${tc.kws[1].msgs[1]}    Process configuration:\n${config}    level=DEBUG

*** Keywords ***
Python script should be run and arguments logged
    [Arguments]    ${arguments}    ${script}=script.py    ${index}=0
    ${script} =    Normalize Path    ${DATADIR}/standard_libraries/process/files/${script}
    ${tc} =    Arguments should be logged    python ${script} ${arguments}    ${index}
    RETURN    ${tc}

Arguments should be logged
    [Arguments]    ${message}    ${index}=0
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[${index}].msgs[0]}    Starting process:\n${message}
    RETURN    ${tc}
