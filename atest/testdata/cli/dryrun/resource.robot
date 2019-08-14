*** Keywords ***
Simple UK
    Log    Hello from UK

Fail In UK
    Fail
    Fail    And again

For Loop in UK
    @{list} =    Create List    1    1    1
    FOR    ${i}    ${j}    ${k}    IN    @{list}
        Should be Equal    ${i}    0
    END
    Fail

Anarchy in the UK
    [Arguments]    ${a1}    ${a2}    ${a3}
    Fail    ${a1}${2}${a3}
