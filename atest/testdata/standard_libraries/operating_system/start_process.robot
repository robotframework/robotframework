*** Settings ***
Suite Setup     My Setup
Suite Teardown  Stop All Processes
Library         OperatingSystem

*** Variables ***
${PROG}  python ${CURDIR}${/}files${/}prog.py
${WRITABLE_PROG}  python ${CURDIR}${/}files${/}writable_prog.py
${TEMP FILE}  ${CURDIR}${/}robot-start-process.tmp

*** Test Cases ***
Start Process
    ${index} =  Start Process  ${PROG} 0 hello
    Equals  ${index}  ${2}
    ${out} =  Read Process Output
    Equals  ${out}  hello
    Start Process  ${PROG} 0 hi
    ${out} =  Read Process Output
    Equals  ${out}  hi

Stderr Is Redirected To Stdout
    Start Process  ${PROG} 0 hey error
    ${out} =  Read Process Output
    Should Match Regexp  ${out}  ^(hey\nerror|error\nhey)$

It Should Be Possble To Start Background Process
    Start Process  ${PROG} 0 hey error &
    ${out} =  Read Process Output
    Should Match Regexp  ${out}  ^(hey\nerror|error\nhey)$

Start Writable Process
    Start Process  ${WRITABLE_PROG}  hello world
    ${output} =  Read Process Output
    Equals  ${output}  HELLO WORLD

Cannot Read From A Stopped Process
    [Documentation]  FAIL Cannot read from a closed process
    Start Process  ${PROG} 0 hello
    ${output} =  Read Process Output
    ${output} =  Read Process Output

Switch Process
    ${first} =  Start Process  ${PROG} 0 hello
    ${second} =  Start Process  ${PROG} 0 world
    Start Process  ${WRITABLE_PROG}  hello world  alias
    Start Process  ${PROG} 0 olleh
    ${output} =  Read Process Output
    Equals  ${output}  olleh
    Switch Process  ${first}
    ${output} =  Read Process Output
    Equals  ${output}  hello
    Switch Process  \ ${second} \
    ${output} =  Read Process Output
    Equals  ${output}  world
    Switch Process  alias
    ${output} =  Read Process Output
    Equals  ${output}  HELLO WORLD

Lives Between Tests Setup
    [Documentation]  Starts a process used in next test case
    Start Process  ${PROG} 0 from_test_case  ${EMPTY}  test case process

Lives Between Tests
    [Setup]  Start Process  ${PROG} 0 from_test_setup  ${EMPTY}  test setup process
    Switch Process  suite setup process
    ${output} =  Read Process Output
    Equals  ${output}  from_suite_setup
    Switch Process  test setup process
    ${output} =  Read Process Output
    Equals  ${output}  from_test_setup
    Switch Process  test case process
    ${output} =  Read Process Output
    Equals  ${output}  from_test_case

Stop All
    [Documentation]  FAIL No active processes
    ${index} =  Start Process  ${PROG} 0 hello
    Start Process  ${PROG} 0 hello
    Stop All Processes
    ${index} =  Start Process  ${PROG} 0 hello
    Equals  ${index}  ${1}
    Stop All Processes
    Read Process Output

Stopping Already Stopped Processes Is OK
    Start Process  ${PROG} 0 hello
    ${output} =  Read Process Output
    Stop Process
    Stop Process
    Start Process  ${PROG} 0 hello
    Stop Process
    Stop Process

Redirecting Stdout To File
    Start Process  ${PROG} 0 hello > ${TEMP FILE}
    Output and Temp File Should Be  ${EMPTY}  hello
    [Teardown]  Remove File  ${TEMP FILE}

Redirecting Stderr To File
    Start Process  ${PROG} 0 hello world 2> ${TEMP FILE}
    Output and Temp File Should Be  hello  world
    [Teardown]  Remove File  ${TEMP FILE}

Redirecting Stderr To Stdout
    Start Process  ${PROG} 0 hello world 2>&1
    Output Should Be  ^(hello\nworld|world\nhello)$

Reading Output With Lot Of Data In Stdout And Stderr
    Start Process  ${PROG} 0 hello world 15000
    ${out} =  Read Process Output
    Length Should Be  ${out}  ${12*15000-1}

*** Keywords ***
My Setup
    ${index} =  Start Process  ${PROG} 0 from_suite_setup  ${EMPTY}  suite setup process
    Equals  ${index}  ${1}

Output And Temp File Should Be
    [Arguments]  ${exp_out}  ${exp_file}
    Output Should Be  ${exp_out}
    Wait Until Keyword Succeeds  2 seconds  0.1 second  Temp File Should Be  ${exp_file}

Output Should Be
    [Arguments]  ${expected}
    ${output} =  Read Process Output
    Stop Process
    Should Match Regexp  ${output}  ^${expected}$

Temp File Should Be
    [Arguments]  ${expected}
    ${file} =  Get File  ${TEMP FILE}
    Should Match Regexp  ${file}  ^${expected}$

