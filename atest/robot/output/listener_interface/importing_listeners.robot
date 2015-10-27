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

Listener With Arguments
    class    listeners.WithArgs    listeners    5
    [Teardown]    Check Listener File    ${ARGS_FILE}
    ...    I got arguments 'value' and 'default'
    ...    I got arguments 'a1' and 'a;2'
    ...    I got arguments 'semi' and 'colons:here'

Listener With Path
    class    ${LISTENERS}${/}ListenAll.py   ListenAll
    [Teardown]    File Should Exist  %{TEMPDIR}${/}${ALL_FILE2}

Listener With Wrong Number Of Arguments
    [Template]    Check Syslog Contains
    Taking listener 'listeners.WithArgs' into use failed:
    ...    Importing listener 'listeners.WithArgs' failed:
    ...    Creating instance failed: TypeError:
    Taking listener 'listeners.WithArgs:1:2:3' into use failed:
    ...    Importing listener 'listeners.WithArgs' failed:
    ...    Creating instance failed: TypeError:

Non Existing Listener
    [Template]    Check Syslog Contains
    Taking listener 'NonExistingListener' into use failed:
    ...    Importing listener 'NonExistingListener' failed:
    ...    ImportError: No module named

Java Listener
    [Tags]  require-jython
    class    JavaListener

Java Listener With Arguments
    [Tags]  require-jython
    class    JavaListenerWithArgs    count=3
    [Teardown]    Check Listener File      ${JAVA_ARGS_FILE}
    ...    I got arguments 'Hello' and 'world'

Java Listener With Wrong Number Of Arguments
    [Tags]  require-jython
    [Template]    Check Syslog Contains
    Taking listener 'JavaListenerWithArgs' into use failed:
    ...    Importing listener 'JavaListenerWithArgs' failed:
    ...    Creating instance failed:
    ...    TypeError: JavaListenerWithArgs(): expected 2 args; got 0${EMPTY TB}
    Taking listener 'JavaListenerWithArgs:b:a:r' into use failed:
    ...    Importing listener 'JavaListenerWithArgs' failed:
    ...    Creating instance failed:
    ...    TypeError: JavaListenerWithArgs(): expected 2 args; got 3${EMPTY TB}


*** Keywords ***

Run Tests With Listeners
    ${listeners} =    Catenate
    ...    --listener ListenAll
    ...    --listener listeners.ListenSome
    ...    --listener module_listener
    ...    --listener listeners.WithArgs:value
    ...    --listener "listeners.WithArgs:a1:a;2"
    ...    --listener "listeners.WithArgs;semi;colons:here"
    ...    --listener ${LISTENERS}${/}ListenAll.py:%{TEMPDIR}${/}${ALL_FILE2}
    ...    --listener listeners.WithArgs
    ...    --listener listeners.WithArgs:1:2:3
    ...    --listener JavaListener
    ...    --listener JavaListenerWithArgs:Hello:world
    ...    --listener JavaListenerWithArgs
    ...    --listener JavaListenerWithArgs:b:a:r
    ...    --listener NonExistingListener
    Run Tests    ${listeners}    misc/pass_and_fail.robot

