*** Keywords ***
Same Twice
    [Documentation]    Having same keyword twice is an error.

Same twice

Same ${embedded}
    [Documentation]    This is an error too.

same ${embedded match}

Invalid arg spec
    [Arguments]    @{varargs}    ${invalid}
