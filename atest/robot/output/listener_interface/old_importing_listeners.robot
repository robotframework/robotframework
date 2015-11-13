*** Settings ***
Suite Setup     Run Tests With Listeners
Resource        listener_resource.robot
Test Template   Check Syslog contains

*** Test Cases ***
Listener API 1 is no longer supported
    Taking listener 'old_listeners.ListenSome' into use failed:
    ...    Listener 'old_listeners.ListenSome' uses unsupported API version 1.
    ...    Switch to API version 2 instead.
    Taking listener 'old_module_listener' into use failed:
    ...    Listener 'old_module_listener' uses unsupported API version 1.
    ...    Switch to API version 2 instead.

Java Listener With Wrong Number Of Arguments
    [Tags]  require-jython
    Taking listener 'OldJavaListener' into use failed:
    ...    Listener 'OldJavaListener' uses unsupported API version 1.
    ...    Switch to API version 2 instead.

*** Keywords ***
Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener old_listeners.ListenSome
    ...    --listener old_module_listener
    ...    --listener OldJavaListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot
