*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/not_keyword_decorator.robot
Resource          atest_resource.robot

*** Test Cases ***
In module
    Check Test Case    ${TESTNAME}
    Not exposed error should be in syslog
    ...    not_exposed_in_module    ModuleWitNotKeywordDecorator

Hide imported function
    Check Test Case    ${TESTNAME}

Set 'robot_not_keyword' attribute directly
    Check Test Case    ${TESTNAME}

Even '@keyword' cannot disable '@not_keyword'
    Check Test Case    ${TESTNAME}

'@not_keyword' is not exposed
    Check Test Case    ${TESTNAME}

'@keyword' is not exposed
    Check Test Case    ${TESTNAME}

'@library' is not exposed
    Check Test Case    ${TESTNAME}

In class
    Check Test Case    ${TESTNAME}
    Not exposed error should be in syslog
    ...    not_exposed_in_class    ClassWithNotKeywordDecorator

In hybrid library
    Check Test Case    ${TESTNAME}
    Not exposed error should be in syslog
    ...    not_exposed_in_hybrid    HybridWithNotKeywordDecorator
    ...    ERROR    Error in

*** Keywords ***
Not exposed error should be in syslog
    [Arguments]    ${keyword}    ${library}    ${level}=INFO    ${prefix}=In
    Syslog should contain
    ...    | ${level.ljust(5)} |
    ...    ${prefix} library '${library}': Adding keyword '${keyword}' failed:
    ...    Not exposed as a keyword.\n
