*** Keywords ***
Get Name
    RETURN    resource1

Get Name With Search Order
    Fail    Should not be run due to search order having higher precedence

Get Best Match Ever With Search Order
    Fail    Should not be run due to search order
    RETURN    fail
