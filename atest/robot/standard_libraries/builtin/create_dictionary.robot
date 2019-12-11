*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/builtin/create_dictionary.robot
Resource         atest_resource.robot

*** Test Cases ***
Empty
    Check Test Case    ${TESTNAME}

Separate keys and values
    Check Test Case    ${TESTNAME}
    Should Be Empty    ${ERRORS}

Separate keys and values using non-string keys
    Check Test Case    ${TESTNAME}

Separate keys and values using list variables
    Check Test Case    ${TESTNAME}

Separate keys and values with escaped equals
    Check Test Case    ${TESTNAME}

Separate keys and values with equals in variable value
    Check Test Case    ${TESTNAME}

Separate keys and values with non-existing variables
    Check Test Case    ${TESTNAME}

Wrong number of separate keys and values
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Separate keys and values with invalid key
    Check Test Case    ${TESTNAME}

`key=value` syntax
    Check Test Case    ${TESTNAME}

`key=value` syntax with non-string keys
    Check Test Case    ${TESTNAME}

`key=value` syntax with escaped equals
    Check Test Case    ${TESTNAME}

`key=value` syntax with equals in variable value
    Check Test Case    ${TESTNAME}

`key=value` syntax with non-existing variables
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

`key=value` syntax with invalid key
    Check Test Case    ${TESTNAME}

`key=value` syntax without equals
    Check Test Case    ${TESTNAME}

Separate keys and values and 'key=value' syntax
    Check Test Case    ${TESTNAME}

`\&{dict}` variable
    Check Test Case    ${TESTNAME}

`\&{dict}` variable with internal variables
    Check Test Case    ${TESTNAME}

Non-existing `\&{dict}` variable
    Check Test Case    ${TESTNAME}

Non-dictionary `\&{dict}` variable
    Check Test Case    ${TESTNAME}
