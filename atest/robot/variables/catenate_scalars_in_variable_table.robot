*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/catenate_scalars_in_variable_table*.robot
Resource         atest_resource.robot

*** Test Cases ***
Default separator is space
    Check Test Case    ${TESTNAME}

Custom separator
    Check Test Case    ${TESTNAME}

Custom separator from variable
    Check Test Case    ${TESTNAME}

Non-string separator
    Check Test Case    ${TESTNAME}

Non-existing variable in separator
    Check Test Case    ${TESTNAME}
    Error In File    0    variables/catenate_scalars_in_variable_table.robot    13
    ...    Setting variable '\${NONEX IN SEP}' failed: Variable '\${NON EXISTING}' not found.

Value containing variables
    Check Test Case    ${TESTNAME}

Value containing list variables
    Check Test Case    ${TESTNAME}

Non-existing variable in value
    Check Test Case    ${TESTNAME}
    Error In File    1    variables/catenate_scalars_in_variable_table.robot    25
    ...    Setting variable '\${NONEX IN VALUE}' failed: Variable '\${NON EXISTING}' not found.

'SEPARATOR=' can be escaped
    Check Test Case    ${TESTNAME}

'SEPARATOR=' must be upper case
    Check Test Case    ${TESTNAME}

'SEPARATOR=' must be first
    Check Test Case    ${TESTNAME}

'SEPARATOR=' cannot come from variable
    Check Test Case    ${TESTNAME}

Having no values creates empty string
    Check Test Case    ${TESTNAME}

One scalar variable is not converted to string
    Check Test Case    ${TESTNAME}

With separator even one scalar variable is converted to string
    Check Test Case    ${TESTNAME}

Catenated in resource
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
