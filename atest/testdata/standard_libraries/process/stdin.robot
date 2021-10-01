*** Settings ***
Library           OperatingSystem
Library           Process

*** Test Cases ***
Stdin is PIPE by defauls
    Start Process    python    -c    import sys; print(sys.stdin.read())
    ${process} =    Get Process Object
    Call Method    ${process.stdin}    write    ${{b'Hello, world!'}}
    Call Method    ${process.stdin}    close
    ${result} =    Wait For Process
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin as PIPE explicitly
    Start Process    python    -c    import sys; print(sys.stdin.read())    stdin=PIPE
    ${process} =    Get Process Object
    Call Method    ${process.stdin}    write    ${{b'Hello, world!'}}
    Call Method    ${process.stdin}    close
    ${result} =    Wait For Process
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be disabled 1
    Start Process    python    -c    import sys; print('Hello, world!')    stdin=NONE
    ${process} =    Get Process Object
    Should Be Equal    ${process.stdin}    ${None}
    ${result} =    Wait For Process
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be disabled 2
    ${result} =    Run Process    python    -c    import sys; print('Hello, world!')    stdin=None
    ${process} =    Get Process Object
    Should Be Equal    ${process.stdin}    ${None}
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be disabled with None object
    ${result} =    Run Process    python    -c    import sys; print('Hello, world!')    stdin=${None}
    ${process} =    Get Process Object
    Should Be Equal    ${process.stdin}    ${None}
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin as file
    Create File    %{TEMPDIR}/stdin.txt    Hyvää päivää maailma!    encoding=CONSOLE
    ${result} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=%{TEMPDIR}/stdin.txt
    Should Be Equal    ${result.stdout}    Hyvää päivää maailma!
    [Teardown]    Remove File    %{TEMPDIR}/stdin.txt

Stdin as text
    ${result} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=Hyvää päivää maailma!
    Should Be Equal    ${result.stdout}    Hyvää päivää maailma!

Stdin as stdout from other process
    Start Process    python    -c    print('Hello, world!')
    ${process} =    Get Process Object
    ${child} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=${process.stdout}
    ${parent} =    Wait For Process
    Should Be Equal   ${child.stdout}    Hello, world!\n
    Should Be Equal   ${parent.stdout}    ${empty}
