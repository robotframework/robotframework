*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/run.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
Run
    Check testcase  Run

Run With RC And Stdout Checks
    Check testcase  Run With RC And Stdout Checks

Run With RC Checks
    Check testcase  Run With RC Checks

Run With Stdout Checks
    Check testcase  Run With Stdout Checks

Run With Stderr
    Check testcase  Run With Stderr

Run With Stderr Redirected To Stdout
    Check testcase  Run With Stderr Redirected To Stdout

Run With Stderr Redirected To File
    Check testcase  Run With Stderr Redirected To File

Run When Command Writes Lot Of Stdout And Stderr
    Check testcase  Run When Command Writes Lot Of Stdout And stderr

Run And Return RC
    Check testcase  Run and return RC

Run And Return RC And Output
    Check testcase  Run and return RC and output

Run Non-ascii Command Returning Non-ascii Output
    Check testcase  Run non-ascii command returning non-ascii output

Trailing Newline Is Removed Automatically
    Check test case  ${TESTNAME}

It Is Possible To Start Background Processes
    Check testcase  It is possible To Start Background Processes

