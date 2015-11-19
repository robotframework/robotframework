*** Settings ***
Suite Setup     Run Tests With Listeners
Resource        listener_resource.robot
Test Template   Check Syslog contains

*** Test Cases ***
Listener API 1 is no longer supported
    Taking listener 'v1_listeners.V1ClassListener' into use failed:
    ...    Listener 'v1_listeners.V1ClassListener' uses unsupported API version 1.
    ...    Switch to API version 2 instead.
    Taking listener 'v1_listeners' into use failed:
    ...    Listener 'v1_listeners' uses unsupported API version 1.
    ...    Switch to API version 2 instead.

Java Listener With Wrong Number Of Arguments
    [Tags]  require-jython
    Taking listener 'OldJavaListener' into use failed:
    ...    Listener 'OldJavaListener' uses unsupported API version 1.
    ...    Switch to API version 2 instead.

*** Keywords ***
Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener v1_listeners.V1ClassListener
    ...    --listener v1_listeners
    ...    --listener OldJavaListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot
