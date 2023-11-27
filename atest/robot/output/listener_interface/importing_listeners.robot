*** Settings ***
Suite Setup     Run Tests With Listeners
Suite Teardown  Remove Listener Files
Resource        listener_resource.robot
Test Template   Listener Import Message Should Be In Syslog

*** Test Cases ***
Python Class Listener From Module With Same Name
    class    ListenAll    ListenAll

Python Class Listener From A Module With Different Name
    class    listeners.ListenSome    listeners

Python Module Listener
    module    module_listener    module_listener

Listener Versions
    [Template]    NONE
    Check Listener File    listener-versions.txt
    ...    V2
    ...    V2AsNonInt
    ...    V3Implicit
    ...    V3Explicit
    ...    V3AsNonInt

Listener With Arguments
    class    listeners.WithArgs    listeners    6
    [Teardown]    Check Listener File    ${ARGS_FILE}
    ...    I got arguments 'value' and 'default'
    ...    I got arguments 'a1' and 'a;2'
    ...    I got arguments 'semi' and 'colons:here'
    ...    I got arguments 'named' and 'args'

Listener With Argument Conversion
    class    listeners.WithArgConversion    listeners    1

Listener With Path
    class    ${LISTENERS}${/}ListenAll.py   ListenAll
    [Teardown]    File Should Exist    %{TEMPDIR}${/}${ALL_FILE2}

Listener With Wrong Number Of Arguments
    [Template]    Importing Listener Failed
    0    listeners.WithArgs          Listener 'WithArgs' expected 1 to 2 arguments, got 0.
    1    listeners.WithArgs:1:2:3    Listener 'WithArgs' expected 1 to 2 arguments, got 3.
Non Existing Listener
    [Template]    Importing Listener Failed
    2    NonExistingListener    *${EMPTY TB}PYTHONPATH:*    pattern=True

Unsupported version
    [Template]    Taking Listener Into Use Failed
    3    unsupported_listeners.V1Listener                Unsupported API version '1'.
    4    unsupported_listeners.V4Listener                Unsupported API version '4'.
    5    unsupported_listeners.InvalidVersionListener    Unsupported API version 'kekkonen'.

*** Keywords ***
Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener ListenAll
    ...    --listener listeners.ListenSome
    ...    --listener module_listener
    ...    --listener listener_versions.V2
    ...    --listener listener_versions.V2AsNonInt
    ...    --listener listener_versions.V3Implicit
    ...    --listener listener_versions.V3Explicit
    ...    --listener listener_versions.V3AsNonInt
    ...    --listener listeners.WithArgs:value
    ...    --listener "listeners.WithArgs:a1:a;2"
    ...    --listener "listeners.WithArgs;semi;colons:here"
    ...    --listener listeners.WithArgs:arg2=args:arg1=named
    ...    --listener listeners.WithArgConversion:42:yes
    ...    --listener ${LISTENERS}${/}ListenAll.py:%{TEMPDIR}${/}${ALL_FILE2}
    ...    --listener listeners.WithArgs
    ...    --listener listeners.WithArgs:1:2:3
    ...    --listener NonExistingListener
    ...    --listener unsupported_listeners.V1Listener
    ...    --listener unsupported_listeners.V4Listener
    ...    --listener unsupported_listeners.InvalidVersionListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot

Importing Listener Failed
    [Arguments]    ${index}    ${name}    ${error}    ${pattern}=False
    VAR    ${error}    Importing listener '${name.split(':')[0]}' failed: ${error}
    Taking Listener Into Use Failed    ${index}    ${name}    ${error}    ${pattern}

Taking Listener Into Use Failed
    [Arguments]    ${index}    ${name}    ${error}    ${pattern}=False
    Check Log Message
    ...    ${ERRORS}[${index}]
    ...    Taking listener '${name}' into use failed: ${error}
    ...    ERROR    pattern=${pattern}
