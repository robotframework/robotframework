*** Keywords ***
Invalid arg spec
    [Arguments]    &{kwargs}    ${invalid}
    No Operation

Same Twice
    [Documentation]    Having same keyword twice is an error.
    No Operation

Same twice
    No Operation

Same ${embedded}
    [Documentation]    This is an error only at run time.
    No Operation

same ${embedded match}
    No Operation
