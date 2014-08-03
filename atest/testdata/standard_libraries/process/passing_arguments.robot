*** Settings ***
Resource          process_resource.robot

*** Test Cases ***
Just command
    ${result} =    Run Process    echo
    Result should equal    ${result}
    ${result} =    Run Process    echo    shell=True
    Result should equal    ${result}

Command and arguments
    ${result} =    Run Process    python    -c    print 'Hello, world!'
    Result should equal    ${result}    stdout=Hello, world!
    ${result} =    Run Process    python    -c    print 'Hi again!'    shell=joo
    Result should equal    ${result}    stdout=Hi again!

Escaping equal sign
    ${result}=    Run Process    python    -c    print 'name\=value'
    Result should equal    ${result}    stdout=name\=value
    ${result}=    Run Process    python -c "print 'shell\=xxx'"    shell=True
    Result should equal    ${result}    stdout=shell=xxx

Unsupported kwargs cause error
    [Template]    Run Keyword And Expect Error
    Keyword argument 'invalid' is not supported by this keyword.
    ...    Run Process    command    shell=True   invalid=argument
    Keyword argument 'shellx' is not supported by this keyword.
    ...    Run Process    command    arg    shellx=True
