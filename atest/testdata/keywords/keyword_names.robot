*** Settings ***
Resource        resources/my_resource_1.robot
Resource        resources/my_resource_2.robot
Library         MyLibrary1

*** Test Cases ***
Test Case File User Keyword Names In Test Case
    Keyword Only In Test Case File
    KeywordONLYinTestCaseFile
    key word on lyin test c asef ile

Resource File User Keyword Names In Test Case
    Keyword Only In Resource 1
    my_resource_1.Keyword ONLY In Resource 1
    My _ Resource _1 . Keywordonly IN res ource 1

Base Keyword Names In Test Case
    Keyword Only In Library 1
    MyLibrary1.keyword_only_in_library_1
    mylibrary1.keywordonlyinlibrary1

Test Case File User Keyword Names In Test Case File User Keyword
    Using Test Case File User Keywords
    Using Test Case File User Keywords Nested

Resource File User Keyword Names In Test Case File User Keyword
    Using Resource File User Keywords
    Using Resource File User Keywords Nested

Base Keyword Names In Test Case File User Keyword
    Using Base Keywords
    Using Base Keywords Nested

Test Case File User Keyword Names In Resource File User Keyword
    Using Test Case File User Keywords In Resource

Resource File User Keyword Names In Resource File User Keyword
    Using Resource File User Keywords In Resource 1
    Using Resource File User Keywords In Resource 2

Base Keyword Names In Resource File User Keyword
    Using Base Keywords In Resource

User Keyword Name Containing Dots
    user keyword.name
    USERKEYWORD. name
    __user__key__word. NAME

User Keyword Name Ending With Dot
    user keyword.
    USER KEYWORD.
    _US_er_ K EY_word .

Name Set Using 'robot_name' Attribute
    Name set using 'robot_name' attribute

Name Set Using 'robot.api.deco.keyword' decorator
    Name set using 'robot.api.deco.keyword' decorator

Custom non-ASCII name
    Custom nön-ÄSCII name

Old Name Doesn't Work If Name Set Using 'robot_name'
    [Documentation]  FAIL No keyword with name 'Name Set In Method Signature' found.
    Name Set In Method Signature

Keyword can just be marked without changing its name
    No Custom Name Given 1
    No Custom Name Given 2

Functions decorated with @keyword can start with underscrore
    I start with an underscore and I am OK
    Function name can be whatever

Embedded Args Keyword
    ${count}  ${item} =  Add 7 Copies of Coffee To Cart
    Should Be Equal  ${count}-${item}  7-Coffee

Assignment is not part of name
    Log    No assignment
    ${var} =    Set Variable    value
    ${v1}    ${v2} =    Set Variable    1    2
    ${first}    @{rest} =    Evaluate    range(10)

Library name and keyword name are separate
    Keyword Only In Test Case File
    Keyword Only In Resource 1
    my_resource_1.keyword only in resource 1
    Log    Hello!
    BuiltIn.LOG    Hillo!

*** Keywords ***
Keyword Only In Test Case File
    Log  Keyword from test case file

User Keyword.Name
    Log  Dot in UK name

User Keyword.
    Log  UK name ending with dot

Using Test Case File User Keywords
    Keyword Only In Test Case File
    KeywordONLYinTestCaseFile
    key word on lyin test c asef ile

Using Test Case File User Keywords Nested
    Using Test Case File User Keywords
    usingtestcasefileuserkeywords

Using Resource File User Keywords
    Keyword Only In Resource 1
    my_resource_1.Keyword ONLY In Resource 1
    My_ Resource_ 1 . Keywordonly IN res ource 1

Using Resource File User Keywords Nested
    Using Resource File User Keywords
    Us I ng resourcefile USERKEYWORDS

Using Base Keywords
    Keyword Only In Library 1
    MyLibrary1.keyword_only_in_library_1
    mylibrary1.keywordonlyinlibrary1

Using Base Keywords Nested
    Using BASE k e y w o rd s
    __us_ingbase_keyw_ord_s__
