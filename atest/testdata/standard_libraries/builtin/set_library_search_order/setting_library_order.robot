*** Settings ***
Suite Setup       Set Library Search Order    Library1    Library2    Library3
Library           TestLibrary.py    Library1    WITH NAME    Library1
Library           TestLibrary.py    Library2    WITH NAME    Library2
Library           TestLibrary.py    Library3    WITH NAME    Library3
Library           TestLibrary.py    Library With Space    WITH NAME    Library With Space
Library           embedded.py
Library           embedded2.py

*** Test Cases ***
Library Order Set In Suite Setup Should Be Available In Test Cases
    Active Library Should Be    Library1

Empty Library Order Can Be Set
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Get Name' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}Library With Space.Get Name
    ...    ${SPACE*4}Library1.Get Name
    ...    ${SPACE*4}Library2.Get Name
    ...    ${SPACE*4}Library3.Get Name
    Set Library Search Order
    Get Name

One Library Can Be Set As Default Library
    Set Library Search Order    Library3
    Active Library Should Be    Library3

More Than One Library Can Be Set As Default Libraries
    Set Library Search Order    Library2    Library1    Library3
    Active Library Should Be    Library2

Non-Existing Libraries In Search Order Are Ignored
    Set Library Search Order    NonEx1    Library2    NonEx2    Library1    Library3
    Active Library Should Be    Library2

Library Order Should Be Available In The Next Test Case
    Active Library Should Be    Library2

Setting Library Order Returns Previous Library Order
    Set Library Search Order    Library1    Library2
    @{library order} =    Set Library Search Order
    Should Be Equal    ${library order}[0]    Library1
    Should Be Equal    ${library order}[1]    Library2

Setting Library Order Allows Setting BuiltIn Library As Default Library
    Set Library Search Order    BuiltIn
    ${result} =    No Operation
    Should Be Equal    ${result}    ${NONE}

Setting Library Order Allows Setting Own Library Before BuiltIn Library
    Set Library Search Order    Library1
    Own Library Should Be Used    Library1

Library Search Order Is Space Insensitive
    Set Library Search Order    Library With Space    Library1    Library3
    Active Library Should Be    Library With Space
    Set Library Search Order    LibraryWithSpace    Library1    Library3
    Active Library Should Be    Library With Space
    Set Library Search Order    Library 3    Library1
    Active Library Should Be    Library3

Library Search Order Is Case Insensitive
    Set Library Search Order    library3    Library1
    Active Library Should Be    Library3

Search Order Controlled Match Containing Embedded Arguments Wins Over Exact Match
    Set Library Search Order    embedded    Library1
    Active Library With Search Order Should Be    embedded

Best Search Order Controlled Match Wins In Library
    Set Library Search Order    embedded2    embedded    Library1
    With Search Order The Best Matching Keyword Should Be Run In    embedded2

*** Keywords ***
Active Library Should Be
    [Arguments]    ${expected}
    ${name} =    Get Name
    Should Be Equal    ${name}    ${expected}

Own Library Should Be Used
    [Arguments]    ${expected}
    ${name} =    No Operation
    Should Be Equal    ${name}    ${expected}

Active Library With Search Order Should Be
    [Arguments]    ${expected}
    ${name} =    Get Name With Search Order
    Should Be Equal    ${name}    ${expected}

With Search Order The Best Matching Keyword Should Be Run In
    [Arguments]    ${expected}
    ${name} =    Get Best Match Ever With Search Order
    Should Be Equal    ${name}    ${expected}
