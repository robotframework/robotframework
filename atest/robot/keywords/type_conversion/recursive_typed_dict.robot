*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    keywords/type_conversion/recursive_typed_dict.robot
Resource          atest_resource.robot

*** Test Cases ***
Recursive TypedDict
    Check Test Case    ${TESTNAME}

Mutually recursive TypedDicts
    Check Test Case    ${TESTNAME}

Invalid recursive TypedDict
    Check Test Case    ${TESTNAME}
