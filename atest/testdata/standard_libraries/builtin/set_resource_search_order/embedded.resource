*** Keywords ***
Get ${Name:\w+}
    Fail    Should not be run due to keywords with normal arguments having higher precedence
    
Get ${Name:\w+} With Search Order
	[Return]    embedded
