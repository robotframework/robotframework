*** Settings ***
Documentation     https://peps.python.org/pep-0649
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/deferred_annotations.robot
Test Tags         require-py3.14
Resource          atest_resource.robot

*** Test Cases ***
Annotation created later
    Check Test Case    ${TESTNAME}

Annotation not available during execution
    Check Test Case    ${TESTNAME}

Annotation not available during execution but is known
    Check Test Case    ${TESTNAME}

Non-existing annotation
    Check Test Case    ${TESTNAME}

Invalid annotation
    Check Log Message    ${ERRORS}[0]    Error in library 'DeferredAnnotations': Adding keyword 'invalid' failed: division by zero    ERROR
