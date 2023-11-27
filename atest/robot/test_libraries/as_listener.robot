*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    ${SOURCES}
Resource        atest_resource.robot

*** Variables ***
${SOURCES}      test_libraries/as_listener/test_scope.robot
...             test_libraries/as_listener/suite_scope.robot
...             test_libraries/as_listener/global_scope.robot
...             test_libraries/as_listener/test_scope_2.robot
...             test_libraries/as_listener/suite_scope_2.robot
...             test_libraries/as_listener/global_scope_2.robot
...             test_libraries/as_listener/multiple_listeners.robot

*** Test Cases ***
Test scope library gets events
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Test scope library gets no previous events
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Suite scope library gets events
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Suite scope library gets previous events in suite
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Global scope library gets events
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Global scope library gets all previous events
    [Documentation]    They don't, however, get events from suites where they are not used.
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

Listener methods in library are keywords
    Check Test Case    ${TESTNAME}

Listener methods starting with underscore are not keywords
    Check Test Case    ${TESTNAME}

Multiple library listeners gets events
    Check Test Case    ${TESTNAME}

All listeners are disabled if one fails
    Check Test Case    ${TESTNAME}

Check closing
    Stderr Should Be Equal To    SEPARATOR=\n
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING TEST SUITE
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING TEST SUITE
    ...    [ ERROR ] Error in library 'lib_not_works': Registering listeners failed: Taking listener 'BadVersionListener' into use failed: Unsupported API version '666'.
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING GLOBAL\n

Library listener should be in syslog
    Syslog Should Contain Regexp    Imported library '.*suite_listenerlibrary.py' with arguments \\[ \\] \\(version <unknown>, class type, SUITE scope, 5 keywords, with listener\\)

Nested scopes
    Run Tests    sources=test_libraries/as_listener/nested_scopes
    Check Test Case    No Listener 1
    Check Test Case    Yes Listener
    Check Test Case    No Listener 2
    Stderr Should Be Equal To    SEPARATOR=\n
    ...    CLOSING TEST CASE (test)
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING TEST SUITE
    ...    CLOSING TEST CASE (suite)
    ...    CLOSING TEST SUITE
    ...    CLOSING GLOBAL\n
