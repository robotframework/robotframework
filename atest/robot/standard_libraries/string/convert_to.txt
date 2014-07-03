*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/string/convert_to.txt
Force Tags        pybot    jybot    regression
Resource          atest_resource.txt

*** Test Cases ***
Convert To Lowercases
    Check Test Case    ${TESTNAME}

Convert To Uppercases
    Check Test Case    ${TESTNAME}
