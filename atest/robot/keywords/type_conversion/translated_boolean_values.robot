*** Settings ***
Suite Setup       Run Tests    --lang fi    keywords/type_conversion/translated_boolean_values.robot
Resource          atest_resource.robot

*** Test Cases ***
Boolean
    Check Test Case    ${TESTNAME}

Via Run Keyword
    Check Test Case    ${TESTNAME}
