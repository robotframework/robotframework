*** Keywords ***
Get ${Name:\w+}
    Fail    Should not be run due to keywords with normal arguments having higher precedence

${Get Name} With Search Order
    Fail    Should not be run due to better match in same resource

Get ${Name:\w+} With Search Order
    RETURN    embedded
