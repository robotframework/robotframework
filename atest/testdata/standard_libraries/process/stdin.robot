*** Settings ***
Resource           process_resource.robot

*** Test Cases ***
Stdin is NONE by default
    ${process} =    Start Process    python    -c    import sys; print('Hello, world!')
    Should Be Equal    ${process.stdin}    ${None}
    ${result} =    Wait For Process
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be set to PIPE
    ${process} =    Start Process    python    -c    import sys; print(sys.stdin.read())    stdin=PIPE
    Call Method    ${process.stdin}    write    ${{b'Hello, world!'}}
    Call Method    ${process.stdin}    close
    ${result} =    Wait For Process
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be disabled explicitly
    ${process} =    Start Process    python    -c    import sys; print('Hello, world!')    stdin=None
    ${result} =    Wait For Process
    Should Be Equal    ${process.stdin}    ${None}
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin can be disabled with None object
    ${process} =    Start Process    python    -c    import sys; print('Hello, world!')    stdin=${None}
    ${result} =    Wait For Process
    Should Be Equal    ${process.stdin}    ${None}
    Should Be Equal    ${result.stdout}    Hello, world!

Stdin as path
    Create File    ${STDIN}    Hyvää päivää maailma!    encoding=CONSOLE
    ${result} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=${STDIN}
    Should Be Equal    ${result.stdout}    Hyvää päivää maailma!
    [Teardown]    Remove File    ${STDIN}

Stdin as `pathlib.Path`
    Create File    ${STDIN}    Hyvää päivää maailma!    encoding=CONSOLE
    ${result} =    Run Process    python    -c    import sys; print(sys.stdin.read())    stdin=${{pathlib.Path($STDIN)}}
    Should Be Equal    ${result.stdout}    Hyvää päivää maailma!
    [Teardown]    Remove File    ${STDIN}

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
