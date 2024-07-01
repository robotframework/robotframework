*** Settings ***
Test Setup         Remove File    ${MESSAGE FILE}
Resource           listener_resource.robot

*** Variables ***
${MESSAGE FILE}    %{TEMPDIR}${/}messages.txt

*** Test Cases ***
Log messages are collected on INFO level by default
    Run Tests    --listener listeners.Messages;${MESSAGE FILE}    misc/pass_and_fail.robot
    Logged messages should be
    ...    INFO: Hello says "Suite Setup"!
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    INFO: Hello says "Pass"!
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    INFO: Hello says "Fail"!
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    FAIL: Expected failure

Log messages are collected on specified level
    Run Tests    -L DEBUG --listener listeners.Messages;${MESSAGE FILE}    misc/pass_and_fail.robot
    Logged messages should be
    ...    INFO: Hello says "Suite Setup"!
    ...    DEBUG: Debug message
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    DEBUG: Argument types are:
    ...    <class 'str'>
    ...    <class 'str'>
    ...    INFO: Hello says "Pass"!
    ...    DEBUG: Debug message
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    DEBUG: Argument types are:
    ...    <class 'str'>
    ...    <class 'str'>
    ...    INFO: Hello says "Fail"!
    ...    DEBUG: Debug message
    ...    INFO: \${assign} = JUST TESTING...
    ...    INFO: \${expected} = JUST TESTING...
    ...    DEBUG: Argument types are:
    ...    <class 'str'>
    ...    <class 'str'>
    ...    FAIL: Expected failure
    ...    DEBUG: Traceback (most recent call last):
    ...    ${SPACE*2}None
    ...    AssertionError: Expected failure

*** Keywords ***
Logged messages should be
    [Arguments]    @{expected}
    Check Listener File    ${MESSAGE FILE}    @{expected}
