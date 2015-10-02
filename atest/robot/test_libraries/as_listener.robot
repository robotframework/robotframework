*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    ${SOURCES}
Resource        atest_resource.robot

*** Variables ***
${SOURCES}      test_libraries/as_listener/suite_scope.robot
...             test_libraries/as_listener/test_scope.robot
...             test_libraries/as_listener/global_scope.robot
...             test_libraries/as_listener/multiple_listeners.robot

*** Test Cases ***
Test scope library gets events
    Check Test Case    ${TESTNAME}

New test gets empty events
    Check Test Case    ${TESTNAME}

Suite scope library gets events
    Check Test Case    ${TESTNAME}

New test gets previous suite scope events
    Check Test Case    ${TESTNAME}

Listener methods in library are keywords
    Check Test Case    ${TESTNAME}

Listener methods starting with underscore are not keywords
    Check Test Case    ${TESTNAME}

Global scope library gets events
    Check Test Case    ${TESTNAME}

New test gets previous global scope events
    Check Test Case    ${TESTNAME}

Multiple library listeners gets events
    Check Test Case    ${TESTNAME}

Check closing
    Stderr Should Match    SEPARATOR=\n
    ...    *CLOSING TEST SUITE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING TEST CASE
    ...    CLOSING GLOBAL

Library listener should be in syslog
    Syslog Should Contain Regexp    Imported library '.*suite_listenerlibrary.py' with arguments \\[ \\] \\(version <unknown>, class type, testsuite scope, 4 keywords, with listener\\)
