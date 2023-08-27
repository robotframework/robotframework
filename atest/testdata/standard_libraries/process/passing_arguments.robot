*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Command and arguments in system
    ${result} =    Run Process    python    ${SCRIPT}    my stdout    my stderr
    Script result should equal    ${result}    stdout=my stdout    stderr=my stderr

Command and arguments in shell as separate arguments
    ${result} =    Run Process    python    ${SCRIPT}    my stdout    shell=True
    Script result should equal    ${result}    stdout=my stdout

Command and arguments in shell as single argument
    ${result} =    Run Process    python ${SCRIPT} my args    shell=joo
    Script result should equal    ${result}    stdout=my    stderr=args

Non-ASCII arguments separately
    ${result} =    Run Process    python    ${ENCODING SCRIPT}    stdout:hyvää    stderr:päivää    encoding:UTF-8
    ...    output_encoding=UTF-8
    Result should equal    ${result}    stdout=hyvää    stderr=päivää

Non-ASCII arguments separately when using shell
    ${result} =    Run Process    python    ${ENCODING SCRIPT}    stdout:hyvää    stderr:päivää    encoding:UTF-8
    ...    output_encoding=UTF-8    shell=True
    Result should equal    ${result}    stdout=hyvää    stderr=päivää

Non-ASCII arguments in as string when using shell
    ${result} =    Run Process    python ${ENCODING SCRIPT} stdout:hyvää stderr:päivää encoding:UTF-8
    ...    output_encoding=UTF-8    shell=True
    Result should equal    ${result}    stdout=hyvää    stderr=päivää

Arguments are converted to strings automatically
    ${result} =    Run Process    python    ${SCRIPT}    ${1}    ${2}    ${3}
    Script result should equal    ${result}    stdout=1    stderr=2    rc=3

Escaping equal sign
    ${result} =    Run Process    python    ${SCRIPT}    name\=value
    Script result should equal    ${result}    stdout=name\=value
    ${result} =    Run Process    python    ${SCRIPT}    shell\=False    shell=True
    Script result should equal    ${result}    stdout=shell=False

Unsupported kwargs cause error
    [Template]    Run Keyword And Expect Error
    Keyword argument 'invalid' is not supported by this keyword.
    ...    Run Process    command    shell=True   invalid=argument
    Keyword argument 'shellx' is not supported by this keyword.
    ...    Run Process    command    arg    shellx=True

Log process config
    Run Process    python -c pass    shell=yes    stdout=%{TEMPDIR}/stdout    cwd=%{TEMPDIR}    alias=äliäs
    Run Process    python    -c    pass    stderr=STDOUT    cwd=${CURDIR}    stdin=PIPE
