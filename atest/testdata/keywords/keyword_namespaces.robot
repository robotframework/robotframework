*** Settings ***
Resource          resources/my_resource_1.robot
Resource          resources/my_resource_2.robot
Library           resources/MyLibrary1.py
Library           resources/MyLibrary2.py    WITH NAME    My With Name
Library           OperatingSystem
Library           String    WITH NAME    Std With Name

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
    My With Name.Keyword In Both Libraries
    MYLIBRARY1. Keyword in ALL Resources and Libraries
    MYWITHNAME. Keyword In All Resources And Libraries
    My Lib Rar Y1. Keyword Everywhere
    mywithname.keywordeverywhere

Non-Unique Keywords Without Full Name Fails 1
    [Documentation]    FAIL
    ...    Multiple keywords with name 'Keyword In Both Resources' found. Give the full name of the keyword you want to use:
    ...    ${SPACE*4}my_resource_1.Keyword In Both Resources
    ...    ${SPACE*4}my_resource_2.Keyword In Both Resources
    Keyword In Both Resources

Non-Unique Keywords Without Full Name Fails 2
    [Documentation]    FAIL Multiple keywords with name 'Keyword In Both Libraries' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}My With Name.Keyword In Both Libraries
    ...    ${SPACE*4}MyLibrary1.Keyword In Both Libraries
    Keyword In Both Libraries

Non-Unique Keywords Without Full Name Fails 3
    [Documentation]    FAIL Multiple keywords with name 'Keyword In All Resources And Libraries' found. \
    ...    Give the full name of the keyword you want to use:
    ...    ${SPACE*4}my_resource_1.Keyword In All Resources And Libraries
    ...    ${SPACE*4}my_resource_2.Keyword In All Resources And Libraries
    Keyword In All Resources And Libraries

Keyword From Test Case File Overrides Keywords From Resources And Libraries
    Keyword Everywhere
    Keyword In TC File Overrides Others

Keyword From Resource Overrides Keywords From Libraries
    Keyword In Resource Overrides Libraries

Keyword From Test Case File Overriding Local Keyword In Resource File Is Deprecated
    Use test case file keyword even when local keyword with same name exists

Local keyword in resource file has precedence over keywords in other resource files
    Use local keyword that exists also in another resource 1
    Use local keyword that exists also in another resource 2

Search order has precedence over local keyword in resource file
    [Setup]    Set library search order    my_resource_1
    Use local keyword that exists also in another resource 1
    Use local keyword that exists also in another resource 2
    [Teardown]    Set library search order

Keyword From Custom Library Overrides Keywords From Standard Library
    Comment
    Copy Directory

Search order can give presedence to standard library keyword over custom keyword
    Set Library Search Order    BuiltIn
    Comment    Used from BuiltIn
    Copy Directory
    [Teardown]    Set Library Search Order

Search order can give presedence to custom keyword over standard library keyword
    Set Library Search Order    MyLibrary1
    Comment
    Copy Directory
    [Teardown]    Set Library Search Order

Keyword From Custom Library Overrides Keywords From Standard Library Even When Std Lib Imported With Different Name
    ${ret} =    Replace String
    Should Be Equal    ${ret}    I replace nothing!
    ${ret} =    My With Name.Replace String
    Should Be Equal    ${ret}    I replace nothing!
    ${ret} =    Std With Name.Replace String    I replace this!    this    that
    Should Be Equal    ${ret}    I replace that!

No Warning When Custom Library Keyword Is Registered As RunKeyword Variant And It Has Same Name As Std Keyword
    Run Keyword If    ${TRUE}    Log    Hello

Keyword In More Than One Custom Library And Standard Library
    [Documentation]    FAIL
    ...    Multiple keywords with name 'No Operation' found. Give the full name of the keyword you want to use:
    ...    ${SPACE*4}BuiltIn.No Operation
    ...    ${SPACE*4}My With Name.No Operation
    ...    ${SPACE*4}MyLibrary1.No Operation
    No Operation

Keywords are first searched from test case file even if they contain dot
    my_resource_1.Overrided in test case file with full name
    BuiltIn.Log    Using keyword in test case file here!

*** Keywords ***
Keyword Only In Test Case File
    Log    Keyword from test case file

Keyword Everywhere
    Log    Keyword from test case file

Keyword In TC File Overrides Others
    Log    Keyword from test case file

Keyword In Test Case And Resource Files
    Log    Keyword from test case file

my_resource_1.Overrided in test case file with full name
    Log    Keyword in test case file overriding keyword in my_resource_1
    Overrided in test case file with full name    # This is from resource

BuiltIn.Log
    [Arguments]    ${arg}
    Log    Keyword in test case file overriding keyword in BuiltIn
    Log    ${arg}    # This is from BuiltIn
