*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Non-ASCII command and output
    ${result}=   Run Process    echo hyvä   shell=True
    Result should equal    ${result}    stdout=hyvä

Non-ASCII command and output with custom stream
    ${result}=   Run Process    echo hyvä   shell=True    stdout=${STDOUT}
    Result should equal    ${result}    stdout=hyvä    stdout_path=${STDOUT}
    [Teardown]   Safe Remove File    ${STDOUT}

Non-ASCII in environment variables
    ${result}=   Run Process    python    -c
    ...    import os, sys; print(os.getenv('X_X').decode(sys.getfilesystemencoding()) \=\= u'hyv\\xe4')
    ...    env:X_X=hyvä    stderr=STDOUT
    Result should equal    ${result}    stdout=True

Trailing newline is removed
    ${result}=   Run Process    python    -c    import sys; sys.stdout.write('nothing to remove')
    Result should equal    ${result}    stdout=nothing to remove
    ${result}=   Run Process    python    -c    import sys; sys.stdout.write('one is removed\\n')
    Result should equal    ${result}    stdout=one is removed
    ${result}=   Run Process    python    -c    import sys; sys.stdout.write('only one is removed\\n\\n\\n')
    Result should equal    ${result}    stdout=only one is removed\n\n

Internal newlines are preserved
    ${result}=   Run Process    python -c "print('1\\n2\\n3')"   shell=True
    Result should equal    ${result}    stdout=1\n2\n3

Newlines with custom stream
    ${result}=   Run Process    python -c "print('1\\n2\\n3')"   shell=True    stdout=${STDOUT}
    Result should equal    ${result}    stdout=1\n2\n3    stdout_path=${STDOUT}
    [Teardown]   Safe Remove File    ${STDOUT}
