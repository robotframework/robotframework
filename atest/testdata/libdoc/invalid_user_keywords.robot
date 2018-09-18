*** Keywords ***
Invalid arg spec
    [Arguments]    &{kwargs}    ${invalid}

Same Twice
    [Documentation]    Having same keyword twice is an error.

Same twice

Same ${embedded}
    [Documentation]    This is an error only at run time.

same ${embedded match}
