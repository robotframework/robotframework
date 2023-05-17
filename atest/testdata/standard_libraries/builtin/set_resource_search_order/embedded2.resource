*** Keywords ***
Get ${Match} With Search Order
    Fail    Should not be run due to a better match in same resource
    RETURN    fail

Get Best ${Match:\w+} With Search Order
    Fail    Should not be run due to a better match in same resource
    RETURN    fail

Get Best ${Match} With Search Order
    Should Be Equal    ${Match}    Match Ever
    RETURN    embedded2
