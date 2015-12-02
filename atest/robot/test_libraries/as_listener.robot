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
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST SUITE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST SUITE
    ...    [ ERROR ] Taking listener 'NoVersionListener' into use for library 'lib_not_works' failed: Listener 'NoVersionListener' does not have mandatory 'ROBOT_LISTENER_API_VERSION' attribute.
    ...    Listeners are disabled for this library.
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING GLOBAL\n

Library listener should be in syslog
    Syslog Should Contain Regexp    Imported library '.*suite_listenerlibrary.py' with arguments \\[ \\] \\(version <unknown>, class type, testsuite scope, 5 keywords, with listener\\)
