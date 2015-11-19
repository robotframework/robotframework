*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  keywords/user_keyword_return_values.robot
Resource        atest_resource.robot

*** Test Cases ***
Return Nothing
    Check Test Case  ${TESTNAME}

Return One String
    Check Test Case  ${TESTNAME}

Return Multiple Strings
    Check Test Case  ${TESTNAME}

Return One Scalar Variable
    Check Test Case  ${TESTNAME}

Return Multiple Scalar Variables
    Check Test Case  ${TESTNAME}

Return Empty List Variable
    Check Test Case  ${TESTNAME}

Return List Variable Containing One Item
    Check Test Case  ${TESTNAME}

Return List Variable Containing Multiple Items
    Check Test Case  ${TESTNAME}

Return Non-Existing Variable
    Check Test Case  ${TESTNAME}

Error About Non-Existing Variable In Return Value Can Be Caught
    Check Test Case  ${TESTNAME}
