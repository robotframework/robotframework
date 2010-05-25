*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  parsing/test_case_and_user_keyword_names.txt
Force Tags      regression  pybot  jybot
Resource        atest_resource.txt

*** Test Cases ***

Test case names are not formatted
    ${tc} =  Check Test Case  test_case names are NOT _forMatted_
    Should Be Equal  ${tc.name}  test_case names are NOT _forMatted_

User keyword names are not formatted
    [Documentation]  Tests also that the name of the keyword is used in log regardless the format how it is used.
    ${tc} =  Check Test Case  ${TESTNAME}
    : FOR  ${i}  IN RANGE  8
    \  Should Be Equal  ${tc.kws[${i}].name}  user_keyword nameS _are_not_ FORmatted

