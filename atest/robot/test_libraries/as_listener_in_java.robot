*** Settings ***
Suite Setup     Run Tests    sources=${SOURCES}
Force Tags      require-jython
Resource        atest_resource.robot

*** Variables ***
${SOURCES}      test_libraries/as_listener/suite_scope_java.robot
...             test_libraries/as_listener/multiple_listeners_java.robot

*** Test Cases ***
Java suite scope library gets events
    Check Test Case    ${TESTNAME}

New java test gets previous suite scope events
    Check Test Case    ${TESTNAME}

Listener methods in library are keywords
    Check Test Case    ${TESTNAME}

Listener methods starting with underscore are not keywords
    Check Test Case    ${TESTNAME}

Multiple library listeners in java gets events
    Check Test Case    ${TESTNAME}

Check closing
    Stderr Should Be Equal To
    ...    SEPARATOR=\n
    ...    CLOSING IN JAVA SUITE LIBRARY LISTENER
    ...    CLOSING IN JAVA SUITE LIBRARY LISTENER
    ...    CLOSING IN JAVA SUITE LIBRARY LISTENER
    ...    CLOSING IN JAVA SUITE LIBRARY LISTENER
    ...    CLOSING IN JAVA SUITE LIBRARY LISTENER\n
