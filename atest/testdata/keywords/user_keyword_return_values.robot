*** Settings ***

*** Test Cases ***
Return Nothing
    ${ret} =  No Return At All
    Equals  ${ret}  ${None}
    ${ret} =  Empty Return
    Equals  ${ret}  ${None}

Return One String
    ${ret} =  Return One String
    Equals  ${ret}  one string

Return Multiple Strings
    ${ret1}  ${ret2}  ${ret3} =  Return Multiple Strings
    Equals  ${ret1}  string 1
    Equals  ${ret2}  string 2
    Equals  ${ret3}  string 3

Return One Scalar Variable
    ${ret} =  Return One Scalar Variable  ret value
    Equals  ${ret}  ret value
    ${ret} =  Return One Scalar Variable  ${42}
    Equals  ${ret}  ${42}

Return Multiple Scalar Variables
    ${ret1}  ${ret2} =  Return Multiple Scalar Variables  ret value  ${42}
    Equals  ${ret1}  ret value
    Equals  ${ret2}  ${42}

Return Empty List Variable
    @{ret} =  Return List Variable
    Fail Unless  @{ret} == []

Return List Variable Containing One Item
    @{ret} =  Return List Variable  one string
    Fail Unless  @{ret} == ['one string']
    ${ret} =  Return List Variable  one string
    Fail Unless  ${ret} == ['one string']

Return List Variable Containing Multiple Items
    @{ret} =  Return List Variable  string  ${42}  ${True}
    Fail Unless  @{ret} == ['string', 42, True]
    ${ret1}  ${ret2} =  Return List Variable  string  ${42}
    Equals  ${ret1}  string
    Equals  ${ret2}  ${42}

Return Non-Existing Variable
    [Documentation]  FAIL  Replacing variables from keyword return value failed: Non-existing variable '\${nonex}'.
    Return Non-Existing Variable


*** Keywords ***
No Return At All
    NOOP

Empty Return
    NOOP

Return One String
    [Return]  one string

Return Multiple Strings
    [Return]  string 1  string 2  string 3

Return One Scalar Variable
    [Arguments]  ${arg}
    [Return]  ${arg}

Return Multiple Scalar Variables
    [Arguments]  ${arg1}  ${arg2}
    [Return]  ${arg1}  ${arg2}

Return List Variable
    [Arguments]  @{args}
    [Return]  @{args}

Return Non-Existing Variable
    [Return]  ${nonex}
