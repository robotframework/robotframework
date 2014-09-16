*** Settings ***
Library         OperatingSystem

*** Variables ***
#               Usage of prog.py: prog.py rc=0 stdout='' stderr='' count=1
${PROG}         python ${CURDIR}${/}files${/}prog.py
${RESULT}       Hyvää üötä

*** Test Cases ***
Run
    [Documentation]  Simply run a program without checking anything
    Run  ${PROG}

Run With RC And Stdout Checks
    ${rc}  ${stdout} =  Run And Return Rc And Output  ${PROG} 42 hello
    Fail Unless Equal  ${stdout}  hello
    Fail Unless Ints Equal  ${rc}  42
    ${rc}  ${stdout} =  Run And Return Rc And Output  ${PROG}
    Fail Unless Ints Equal  ${rc}  0
    Fail Unless Equal  ${stdout}  \

Run With RC Checks
    Run and Check RC  ${PROG} 42 hello  42
    Run and Check RC  ${PROG}  0
    Run and Check RC  ${PROG} -1  255
    Run and Check RC  ${PROG} 266 hello  10
    Run and Check RC  ${PROG} 1000000  64
    Run and Check RC  ${PROG} 256  0

Run With Stdout Checks
    ${stdout} =  Run  ${PROG} 42 hello
    Should Be Equal  ${stdout}  hello
    ${stdout} =  Run  ${PROG}
    Should Be Equal  ${stdout}  ${EMPTY}
    Comment  Check that trailing newline is removed  In Windows echo adds extra space
    ${stdout} =  Run  echo hello world
    Should Match Regexp  ${stdout}  ^hello world ?$

Run With Stderr
    [Documentation]  Possible stderr from executed command is redirected to stdout with "2>&1" unless the command has it's own redirect.
    ${output} =  Run  ${PROG} 42 hello world
    Fail Unless Regexp Matches  ${output}  ^(hello\nworld|world\nhello)$

Run With Stderr Redirected To Stdout
    [Documentation]  Explicit redirect i.e. exactly same end results as with above test
    ${output} =  Run  ${PROG} 42 hello world 2>&1
    Fail Unless Regexp Matches  ${output}  ^(hello\nworld|world\nhello)$

Run With Stderr Redirected To File
    [Documentation]  Stderr is redirected to a file using syntax "2>stderr.txt"
    ${temp} =  Join Path  %{TEMPDIR}  robot_test_stderr.txt
    ${stdout} =  Run  ${PROG} 42 hello world 2>${temp}
    Equals  ${stdout}  hello
    ${stderr} =  Get File  ${temp}
    Equals  ${stderr}  world\n
    [Teardown]  Remove File  ${temp}

Run When Command Writes Lot Of Stdout And Stderr
    ${stdout} =  Run  ${PROG} 0 out err 20000
    Length Should Be  ${stdout}  159999

Run And Return RC
    ${rc} =  Run And Return RC  ${PROG} 42 hello
    Equals  ${rc}  ${42}

Run And Return RC And Output
    ${rc}  ${output} =  Run And Return RC And Output  ${PROG} 42 hello
    Equals  ${rc}  ${42}
    Equals  ${output}  hello

Run Non-ascii Command Returning Non-ascii Output
    ${output} =  Run  echo ${result}
    Should Be Equal  ${output.strip()}  ${result}

Trailing Newline Is Removed Automatically
    ${output} =  Run  echo hello
    Log  ${output.__repr__()}
    Should Be True  '${output}'[-1] not in ['\\n', '\\r']

It Is Possible To Start Background Processes
    ${output} =  Run  ${PROG} 0 foo bar&
    Should Contain  ${output}  foo
    Should Contain  ${output}  bar

*** Keywords ***
Run And Check RC
    [Arguments]  ${command}  ${expected}
    ${rc} =  Run And Return Rc  ${command}
    ${expected} =  Convert To Integer  ${expected}
    Should Be Equal  ${rc}  ${expected}

