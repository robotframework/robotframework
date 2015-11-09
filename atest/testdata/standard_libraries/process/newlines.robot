*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
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
