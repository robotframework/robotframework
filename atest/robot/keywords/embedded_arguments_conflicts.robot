*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/embedded_arguments_conflicts.robot
Resource          atest_resource.robot

*** Test Cases ***
Unique match in suite file
    Check Test Case    ${TESTNAME}

Best match wins in suite file
    Check Test Case    ${TESTNAME}

Conflict in suite file
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Unique match in resource
    Check Test Case    ${TESTNAME}

Best match wins in resource
    Check Test Case    ${TESTNAME}

Conflict in resource
    Check Test Case    ${TESTNAME}

Unique match in resource with explicit usage
    Check Test Case    ${TESTNAME}

Best match wins in resource with explicit usage
    Check Test Case    ${TESTNAME}

Conflict in resource with explicit usage
    Check Test Case    ${TESTNAME}

Unique match in library
    Check Test Case    ${TESTNAME}

Best match wins in library
    Check Test Case    ${TESTNAME}

Conflict in library
    Check Test Case    ${TESTNAME}

Unique match in library with explicit usage
    Check Test Case    ${TESTNAME}

Best match wins in library with explicit usage
    Check Test Case    ${TESTNAME}

Conflict in library with explicit usage
    Check Test Case    ${TESTNAME}

Search order resolves conflict with resources
    Check Test Case    ${TESTNAME}

Search order wins over best match in resource
    Check Test Case    ${TESTNAME}

Search order resolves conflict with libraries
    Check Test Case    ${TESTNAME}

Search order wins over best match in libraries
    Check Test Case    ${TESTNAME}

Search order cannot resolve conflict within resource
    Check Test Case    ${TESTNAME}

Search order causes conflict within resource
    Check Test Case    ${TESTNAME}

Search order cannot resolve conflict within library
    Check Test Case    ${TESTNAME}

Search order causes conflict within library
    Check Test Case    ${TESTNAME}

Public match wins over better private match in different resource
    Check Test Case    ${TESTNAME}

Match in same resource wins over better match elsewhere
    Check Test Case    ${TESTNAME}

Keyword without embedded arguments wins over keyword with them in same file
    Check Test Case    ${TESTNAME}

Keyword without embedded arguments wins over keyword with them in different file
    Check Test Case    ${TESTNAME}
