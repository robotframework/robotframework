*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/using_dict_variables.robot
Resource         atest_resource.robot

*** Test Cases ***
From variable table
    Check Test Case    ${TESTNAME}

From variable file
    Check Test Case    ${TESTNAME}

From keyword return value
    Check Test Case    ${TESTNAME}

Escaped dict
    Check Test Case    ${TESTNAME}

Escaped items in dict
    Check Test Case    ${TESTNAME}

Multiple dict variables
    Check Test Case    ${TESTNAME}

Multiple dict variables with same names multiple times
    Check Test Case    ${TESTNAME}

Internal variables
    Check Test Case    ${TESTNAME}

Extended variables
    Check Test Case    ${TESTNAME}

Converted to string if not alone
    Check Test Case    ${TESTNAME}

Use as list
    Check Test Case    ${TESTNAME}

Using with named
    Check Test Case    ${TESTNAME}

Using with non-existing keys
    Check Test Case    ${TESTNAME}

Using when no named or kwargs accepted
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Positional after
    Check Test Case    ${TESTNAME}

Non-existing
    Check Test Case    ${TESTNAME}

Non-dictionary
    Check Test Case    ${TESTNAME}

Non-string keys
    Check Test Case    ${TESTNAME}

Dicts are ordered but order does not affect equality
    Check Test Case    ${TESTNAME}
