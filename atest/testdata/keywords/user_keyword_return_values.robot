*** Test Cases ***
Return Nothing
    ${ret} =  No Return At All
    Should Be Equal  ${ret}  ${None}
    ${ret} =  Empty Return
    Should Be Equal  ${ret}  ${None}

Return One String
    ${ret} =  Return One String
    Should Be Equal  ${ret}  one string

Return Multiple Strings
    ${ret1}  ${ret2}  ${ret3} =  Return Multiple Strings
    Should Be Equal  ${ret1}  string 1
    Should Be Equal  ${ret2}  string 2
    Should Be Equal  ${ret3}  string 3

Return One Scalar Variable
    ${ret} =  Return One Scalar Variable  ret value
    Should Be Equal  ${ret}  ret value
    ${ret} =  Return One Scalar Variable  ${42}
    Should Be Equal  ${ret}  ${42}

Return Multiple Scalar Variables
    ${ret1}  ${ret2} =  Return Multiple Scalar Variables  ret value  ${42}
    Should Be Equal  ${ret1}  ret value
    Should Be Equal  ${ret2}  ${42}

Return Empty List Variable
    @{ret} =  Return List Variable
    Should Be True  @{ret} == []

Return List Variable Containing One Item
    @{ret} =  Return List Variable  one string
    Should Be True  @{ret} == ['one string']
    ${ret} =  Return List Variable  one string
    Should Be True  ${ret} == ['one string']

Return List Variable Containing Multiple Items
    @{ret} =  Return List Variable  string  ${42}  ${True}
    Should Be True  @{ret} == ['string', 42, True]
    ${ret1}  ${ret2} =  Return List Variable  string  ${42}
    Should Be Equal  ${ret1}  string
    Should Be Equal  ${ret2}  ${42}

Return Non-Existing Variable
    [Documentation]  FAIL  Replacing variables from keyword return value failed: Variable '\${nonexisting}' not found.
    Return Non-Existing Variable

Error About Non-Existing Variable In Return Value Can Be Caught
    Run Keyword And Ignore Error    Return Non-Existing Variable
    Run Keyword And Expect Error
    ...    Replacing variables from keyword return value failed: Variable '\${nonexisting}' not found.
    ...    Return Non-Existing Variable


*** Keywords ***
No Return At All
    No Operation

Empty Return
    [Return]
    No Operation

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
    [Return]  ${nonexisting}
