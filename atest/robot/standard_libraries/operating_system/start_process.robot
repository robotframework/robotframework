*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/start_process.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Start Process
    Check Test Case  Start Process

Stderr Is Redirected To Stdout
    Check Test Case  Stderr Is Redirected To Stdout

It Should Be Possble To Start Background Process
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

