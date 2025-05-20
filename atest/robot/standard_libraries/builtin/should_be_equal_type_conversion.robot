*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/builtin/should_be_equal_type_conversion.robot
Resource          atest_resource.robot

*** Test Cases ***
Convert second argument using `type`
    Check Test Case    ${TESTNAME}

Automatic `type`
    Check Test Case    ${TESTNAME}

Automatic `type` doesn't handle nested types
    Check Test Case    ${TESTNAME}

First argument must match `type`
    Check Test Case    ${TESTNAME}

Conversion fails with `type`
    Check Test Case    ${TESTNAME}

Invalid type with `type`
    Check Test Case    ${TESTNAME}

Convert both arguments using `types`
    Check Test Case    ${TESTNAME}

Conversion fails with `types`
    Check Test Case    ${TESTNAME}

Invalid type with `types`
    Check Test Case    ${TESTNAME}

Cannot use both `type` and `types`
    Check Test Case    ${TESTNAME}

Automatic type doesn't work with `types`
    Check Test Case    ${TESTNAME}
