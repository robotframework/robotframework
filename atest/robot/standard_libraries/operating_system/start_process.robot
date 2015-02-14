*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/start_process.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Variables ***
${DEPRECATED}   Keyword 'OperatingSystem.Start Process' is deprecated. Use `Process.Start Process` instead.

*** Test Cases ***
Start Process
    Check Test Case  Start Process

Stderr Is Redirected To Stdout
    Check Test Case  Stderr Is Redirected To Stdout

It Should Be Possble To Start Background Process
    Run Keyword If    "${JYTHON}"    Remove Tags    regression
    Check Test Case  It should Be Possble To Start Background Process

Start Writable Process
    Check Test Case  Start Writable Process

Cannot Read From A Stopped Process
    Check Test Case  Cannot Read From A Stopped Process

Switch Process
    Check Test Case  Switch Process

Lives Between Tests
    Check Test Case  Lives Between tests

Stop All
    Check Test Case  Stop All

Stopping Already Stopped Processes Is OK
    Check Test Case  Stopping Already Stopped Processes Is OK

Redirecting Stdout To File
    Check Test Case  Redirecting Stdout To File

Redirecting Stderr To File
    Check Test Case  Redirecting Stderr To File

Redirecting Stderr To Stdout
    Check Test Case  Redirecting stderr To Stdout

Reading Output With Lot Of Data In Stdout And Stderr
    Check Test Case  Reading Output With Lot Of Data In Stdout And Stderr

Start Process keyword is deprecated
    ${tc} =    Check Test Case    Start Process
    Check Log Message    ${tc.kws[0].msgs[0]}    ${DEPRECATED}    WARN
    Length Should Be    ${ERRORS}    22
    :FOR    ${error}    IN    @{ERRORS}
    \    Check Log Message    ${error}    ${DEPRECATED}    WARN
