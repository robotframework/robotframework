*** Settings ***
Suite Setup       Set Library Search Order    resource1    resource2
Resource          resource1.robot
Resource          resource2.robot
Resource          embedded.resource
Resource          embedded2.resource
Library           ../set_library_search_order/TestLibrary.py
Library           ../set_library_search_order/TestLibrary.py    AnotherLibrary    WITH NAME    AnotherLibrary

*** Test Cases ***
Resource Order Set In Suite Setup Should Be Available In Test Cases
    Active Resource Should Be    resource1

Empty Resource Order Can Be Set
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Get Name' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}resource1.Get Name
    ...    ${SPACE*4}resource2.Get Name
    Set Library Search Order
    Get Name

One Resource Can Be Set As Default Resource
    Set Library Search Order    resource2
    Active Resource Should Be    resource2

More Than One Resources Can Be Set As Default Resources
    Set Library Search Order    resource1    resource2
    Active Resource Should Be    resource1

Non-Existing Resources In Search Order Are Ignored
    Set Library Search Order    nonex1    resource1    nonex2    resource2
    Active Resource Should Be    resource1

Resource Order Should Be Available In The Next Test Case
    Active Resource Should Be    resource1

Setting Resource Order Returns Previous Resource Order
    Set Library Search Order    resource2    resource1
    @{order} =    Set Library Search Order
    Should Be Equal    ${order}[0]    resource2
    Should Be Equal    ${order}[1]    resource1

It Is Possible To Set Both Library And Resource Priorities At The Same Time
    Set Library Search Order    resource1    resource2    TestLibrary    AnotherLibrary
    Active Resource Should Be    resource1
    Active Library Should be    TestLibrary

Resources Always Have Higher Priority Than Libraries
    Set Library Search Order    TestLibrary    AnotherLibrary    resource1    resource2
    Active Resource Should Be    resource1
    Active Library Should be    TestLibrary

Resource Search Order Is Space Insensitive
    Set Library Search Order    resource 1    resource2
    Active Resource Should Be    resource1

Resource Search Order Is Case Insensitive
    Set Library Search Order    Resource1    resource2
    Active Resource Should Be    resource1

Search Order Controlled Match Containing Embedded Arguments Wins Over Exact Match
    Set Library Search Order    embedded    resource1
    With Search Order Active Resource Should Be    embedded

Best Search Order Controlled Match Wins In Resource
    Set Library Search Order    embedded2    embedded    resource1
    With Search Order The Best Matching Keyword Should Be Run In    embedded2

*** Keywords ***
Active Resource Should Be
    [Arguments]    ${expected}
    ${name} =    Get Name
    Should Be Equal    ${name}    ${expected}

Active Library Should Be
    [Arguments]    ${expected}
    ${name} =    Get Library Name
    Should Be Equal    ${name}    ${expected}

With Search Order Active Resource Should Be
    [Arguments]    ${expected}
    ${name} =    Get Name With Search Order
    Should Be Equal    ${name}    ${expected}

With Search Order The Best Matching Keyword Should Be Run In
    [Arguments]    ${expected}
    ${name} =    Get Best Match Ever With Search Order
    Should Be Equal    ${name}    ${expected}
