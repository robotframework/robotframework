*** Settings ***
Resource          resources/my_resource_1.robot
Resource          resources/my_resource_2.robot
Library           resources/MyLibrary1.py
Library           resources/MyLibrary2.py
Library           OperatingSystem
Library           String    WITH NAME    Std Lib With Custom Name

*** Test Cases ***
Keywords With Unique Name Are Ok
    Keyword Only In Test Case File
    KeywordOnlyInResource1
    keywordonlyinresource2
    Key Word _ONLY_ In Library 1
    KEYWORDONLYINLIBRARY2

Full Name Works With Non-Unique Keyword Names
    my_resource_1.Keyword In Both Resources
    My_Resource_2.Keyword In Both Resources
    MY_RES Ource _1.Keyword In All Resources And Libraries
    my_ RESOURCE _ 2.Keyword in all RESOURCES and libraries
    MY _ RES ource _ 1 . Keyword Every WHERE
    my_ resource_2.keyword everywhere
    MyLibrary1.Keyword In Both Libraries
    My Library 2.Keyword In Both Libraries
    MYLIBRARY1. Keyword in ALL Resources and Libraries
    MYLIBRARY2. Keyword In All Resources And Libraries
    My Lib Rar Y1. Keyword Everywhere
    mylibrary2.keywordeverywhere

Non-Unique Keywords Without Full Name Fails 1
    [Documentation]    FAIL Multiple keywords with name 'Keyword In Both Resources' found.
    ...    Give the full name of the keyword you want to use.
    ...    Found: 'my_resource_1.Keyword In Both Resources' and 'my_resource_2.Keyword In Both Resources'
    Keyword In Both Resources

Non-Unique Keywords Without Full Name Fails 2
    [Documentation]    FAIL Multiple keywords with name 'Keyword In Both Libraries' found.
    ...    Give the full name of the keyword you want to use.
    ...    Found: 'MyLibrary1.Keyword In Both Libraries' and 'MyLibrary2.Keyword In Both Libraries'
    Keyword In Both Libraries

Non-Unique Keywords Without Full Name Fails 3
    [Documentation]    FAIL Multiple keywords with name 'Keyword In All Resources And Libraries' found.
    ...    Give the full name of the keyword you want to use.
    ...    Found: 'my_resource_1.Keyword In All Resources And Libraries' and 'my_resource_2.Keyword In All Resources And Libraries'
    Keyword In All Resources And Libraries

Keyword From Test Case File Overrides Keywords From Resources And Libraries
    Keyword Everywhere
    Keyword In TC File Overrides Others

Keyword From Resource Overrides Keywords From Libraries
    Keyword In Resource Overrides Libraries

Keyword From User Library Overrides Keywords From Standard Library
    Comment
    Copy Directory

Keyword From User Library Overrides Keywords From Standard Library Even When Std Lib Imported With Different Name
    ${ret} =    Replace String
    Should Be Equal    ${ret}    I replace nothing!
    ${ret} =    MyLibrary1.Replace String
    Should Be Equal    ${ret}    I replace nothing!
    ${ret} =    Std Lib With Custom Name.Replace String    I replace this!    this    that
    Should Be Equal    ${ret}    I replace that!

No Warning When User Library Keyword Is Registered As RunKeyword Variant And It Has Same Name As Std Keyword
    Run Keyword If    ${TRUE}    Log    Hello

Keyword In More Than One User Library And Standard Library
    [Documentation]    FAIL Multiple keywords with name 'No Operation' found.
    ...    Give the full name of the keyword you want to use.
    ...    Found: 'BuiltIn.No Operation', 'MyLibrary1.No Operation' and 'MyLibrary2.No Operation'
    No Operation

*** Keywords ***
Keyword Only In Test Case File
    Log    Keyword from test case file

Keyword Everywhere
    Log    Keyword from test case file

Keyword In TC File Overrides Others
    Log    Keyword from test case file

Keyword In Test Case And Resource Files
    Log    Keyword from test case file
