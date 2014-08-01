*** Settings ***
Resource        resources/my_resource_1.html
Resource        resources/my_resource_2.html
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

