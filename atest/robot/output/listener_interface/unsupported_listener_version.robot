*** Settings ***
Suite Setup     Run Tests With Listeners
Resource        listener_resource.robot
Test Template   Check Syslog contains

*** Test Cases ***
Listener API 1 is no longer supported
    Taking listener 'unsupported_listeners.V1ClassListener' into use failed:
    ...    Unsupported API version '1' in listener 'unsupported_listeners.V1ClassListener'.
    Taking listener 'unsupported_listeners.InvalidVersionClassListener' into use failed:
    ...    Unsupported API version 'kekkonen' in listener 'unsupported_listeners.InvalidVersionClassListener'.
    Taking listener 'unsupported_listeners' into use failed:
    ...    Listener 'unsupported_listeners' does not specify API version.
    ...    Attribute 'ROBOT_LISTENER_API_VERSION' is required.

Java Listener With Wrong Number Of Arguments
    [Tags]  require-jython
    Taking listener 'OldJavaListener' into use failed:
    ...    Listener 'OldJavaListener' does not specify API version.
    ...    Attribute 'ROBOT_LISTENER_API_VERSION' is required.

*** Keywords ***
Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener unsupported_listeners.V1ClassListener
    ...    --listener unsupported_listeners.InvalidVersionClassListener
    ...    --listener unsupported_listeners
    ...    --listener OldJavaListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot
