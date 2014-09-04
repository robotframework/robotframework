*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/subtract_date_from_date.txt
Force Tags       regression    pybot    jybot
Resource         atest_resource.txt

*** Test Cases ***
Subtraction between two dates should succeed
    Check Test Case    ${TESTNAME}
