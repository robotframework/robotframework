*** Settings ***
Suite Setup     Run Tests With Listeners
Suite Teardown  Remove Listener Files
Force Tags      regression
Default Tags    pybot  jybot
Resource        listener_resource.robot
Test Template   Listener Import Message Should Be In Syslog

*** Test Cases ***
Python Class Listener From Module With Same Name
    class    OldListenAll    OldListenAll    deprecated=0

Python Class Listener From A Module With Different Name
    class    old_listeners.ListenSome    old_listeners    deprecated=1

Python Module Listener
    module    old_module_listener    old_module_listener    deprecated=2

Listener With Arguments
    class    old_listeners.WithArgs    old_listeners    4    deprecated=3
    [Teardown]    Check Listener File  ${ARGS_FILE}
    ...    I got arguments 'value' and 'default'    I got arguments 'a1' and 'a2'

Listener With Path
    class    ${LISTENERS}${/}OldListenAll.py    OldListenAll    deprecated=5
    [Teardown]    File Should Exist  %{TEMPDIR}${/}${ALL_FILE2}

Listener With Wrong Number Of Arguments
    [Template]    Check Syslog contains
    Taking listener 'old_listeners.WithArgs' into use failed:
    ...    Importing listener 'old_listeners.WithArgs' failed:
    ...    Creating instance failed: TypeError:
    Taking listener 'old_listeners.WithArgs:1:2:3' into use failed:
    ...    Importing listener 'old_listeners.WithArgs' failed:
    ...    Creating instance failed: TypeError:

Non Existing Listener
    [Template]    NONE
    Run on python 2.x
    ...    Check Syslog contains
    ...    Taking listener 'NonExistingListener' into use failed:
    ...    Importing listener 'NonExistingListener' failed:
    ...    ImportError: No module named NonExistingListener${EMPTY TB}
    Run on python 3.x
    ...    Check Syslog contains
    ...    Taking listener 'NonExistingListener' into use failed:
    ...    Importing listener 'NonExistingListener' failed:
    ...    ImportError: No module named 'NonExistingListener'${EMPTY TB}

Java Listener
    [Tags]  jybot
    class    OldJavaListener    deprecated=8

Java Listener With Arguments
    [Tags]  jybot
    class    OldJavaListenerWithArgs    count=3    deprecated=9
    [Teardown]    Check Listener File    ${JAVA_ARGS_FILE}
    ...    I got arguments 'Hello' and 'world'

Java Listener With Wrong Number Of Arguments
    [Tags]  jybot
    [Template]    Check Syslog contains
    Taking listener 'OldJavaListenerWithArgs' into use failed:
    ...    Importing listener 'OldJavaListenerWithArgs' failed:
    ...    Creating instance failed:
    ...    TypeError: OldJavaListenerWithArgs(): expected 2 args; got 0${EMPTY TB}
    Taking listener 'OldJavaListenerWithArgs:b:a:r' into use failed:
    ...    Importing listener 'OldJavaListenerWithArgs' failed:
    ...    Creating instance failed:
    ...    TypeError: OldJavaListenerWithArgs(): expected 2 args; got 3${EMPTY TB}

*** Keywords ***

Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener OldListenAll
    ...    --listener old_listeners.ListenSome
    ...    --listener old_module_listener
    ...    --listener old_listeners.WithArgs:value
    ...    --listener old_listeners.WithArgs:a1:a2
    ...    --listener ${LISTENERS}${/}OldListenAll.py:%{TEMPDIR}${/}${ALL_FILE2}
    ...    --listener old_listeners.WithArgs
    ...    --listener old_listeners.WithArgs:1:2:3
    ...    --listener OldJavaListener
    ...    --listener OldJavaListenerWithArgs:Hello:world
    ...    --listener OldJavaListenerWithArgs
    ...    --listener OldJavaListenerWithArgs:b:a:r
    ...    --listener NonExistingListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot
