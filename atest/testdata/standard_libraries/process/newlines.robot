*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Trailing newline is removed
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('nothing to remove')
    Result should equal    ${result}    stdout=nothing to remove
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('removed\\n')
    Result should equal    ${result}    stdout=removed
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('only one is removed\\n\\n\\n')
    Result should equal    ${result}    stdout=only one is removed\n\n

Internal newlines are preserved
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('1\\n2\\n3\\n')
    Result should equal    ${result}    stdout=1\n2\n3

CRLF is converted to LF
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('1\\r\\n2\\r3\\n4')
    # On Windows \r\n is turned \r\r\n when writing and thus the result is \r\n.
    # Elsewhere \r\n is not changed when writing and thus the result is \n.
    # ${\n} is \r\n or \n depending on the OS and thus works as the expected result.
    Result should equal    ${result}    stdout=1${\n}2\r3\n4

Newlines with custom stream
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('1\\n2\\n3\\n')
    Result should equal    ${result}    stdout=1\n2\n3
    ${result}=    Run Process    python    -c    import sys; sys.stdout.write('1\\n2\\r\\n3\\n')    stdout=${STDOUT}
    Result should equal    ${result}    stdout=1\n2${\n}3    stdout_path=${STDOUT}
    ${output} =    Get Binary File    ${STDOUT}
    Should Be Equal    ${output}    1${\n}2\r${\n}3${\n}    type=bytes
    [Teardown]    Safe Remove File    ${STDOUT}
