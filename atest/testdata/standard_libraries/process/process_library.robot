*** Settings ***
Suite Setup       Some process    suite_process
Suite Teardown    Stop some process    suite_process
Test Setup        Restart Suite Process If Needed
Resource          resource.robot

*** Test Cases ***
Library Namespace should be global
    Process Should Be Running    suite_process

Running a process
    ${result}=    Run Python Process    import sys; sys.stdout.write('hello')
    Result should equal    ${result}    stdout=hello

Error in exit code and stderr output
    ${result}=    Run Python Process    1/0
    Result should match    ${result}    stderr=*ZeroDivisionError: integer division or modulo by zero*    rc=1

Start And Wait Process
    ${handle}=    Start Python Process    import time;time.sleep(0.1)
    Process Should Be Running    ${handle}
    Wait For Process    ${handle}
    Process Should Be Stopped    ${handle}

Change Current Working Directory
    ${result}=    Run Process    python    -c    import os; print os.path.abspath(os.curdir);    cwd=.
    ${result2}=    Run Process    python    -c    import os; print os.path.abspath(os.curdir);    cwd=..
    Should Not Be Equal    ${result.stdout}    ${result2.stdout}

Unsupported Arguments Should Cause Error
    [Template]    Run Keyword And Expect Error
    Keyword argument 'invalid' is not supported by this keyword.
    ...    Run Process    echo foo    shell=True   invalid=argument
    Keyword argument 'shellx' is not supported by this keyword.
    ...    Run Process    echo foo    shellx=True

Escaping equals sign
    ${result}=    Run Process    python    -c    print 'stderr\=bar.buu'    shell=True
    Result should match    ${result}    stdout=*stderr=bar.buu*

Running a process in a shell
    ${result}=    Run Process    python -c "print 'hello'"    shell=True
    Result should equal    ${result}    stdout=hello
    ${result}=    Run Process    python -c "print 'hello'"    shell=0
    Result should equal    ${result}    stdout=hello
    Run Keyword And Expect Error    *    Run Process    python -c "print 'hello'"    shell=${False}
    Run Keyword And Expect Error    *    Run Process    python -c "print 'hello'"    shell=${0}
    Run Keyword And Expect Error    *    Run Process    python -c "print 'hello'"    shell=False
    Run Keyword And Expect Error    *    Run Process    python -c "print 'hello'"    shell=false

Input things to process
    Start Process    python -c "print 'inp %s' % raw_input()"    shell=True
    ${process}=    Get Process Object
    Log   ${process.stdin.write("some input\n")}
    Log   ${process.stdin.flush()}
    ${result}=    Wait For Process
    Should Match    ${result.stdout}    *inp some input*

Get process id
    Check Precondition    not sys.platform.startswith('java')
    ${handle}=    Some process
    ${pid}=    Get Process Id    ${handle}
    Should Not Be Equal   ${pid}   ${None}
    Evaluate    os.kill(int(${pid}),signal.SIGTERM) if hasattr(os, 'kill') else os.system('taskkill /pid ${pid} /f')    os,signal
    Wait For Process    ${handle}

*** Keywords ***
Restart Suite Process If Needed
    ${alive}=    Is Process Running    suite_process
    Run Keyword Unless    ${alive}    Some process    suite_process
