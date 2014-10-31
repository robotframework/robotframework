*** Settings ***
Documentation     Tests for how keyword names are logged in outputs. Should
...               always use full names (e.g. 'MyLib.My Keyword') and use format
...               defined in library or resource, not format that is used.
Suite Setup       Run Tests    --pythonpath ${RESDIR}    keywords/keyword_names.robot
Force Tags        regression    jybot    pybot
Resource          atest_resource.robot

*** Variables ***
${RESDIR}         ${DATADIR}/keywords/resources

*** Test Cases ***
Test Case File User Keyword Names In Test Case
    Check Test And Three Keyword Names    Test Case File User Keyword Names In Test Case    Keyword Only In Test Case File

Resource File User Keyword Names In Test Case
    Check Test And Three Keyword Names    Resource File User Keyword Names In Test Case    my_resource_1.Keyword Only In Resource 1

Base Keyword Names In Test Case
    Check Test And Three Keyword Names    Base Keyword Names In Test Case    MyLibrary1.Keyword Only In Library 1

Test Case File User Keyword Names In Test Case File User Keyword
    ${test} =    Check Test Case    Test Case File User Keyword Names In Test Case File User Keyword
    Check Name and Three Keyword Names    ${test.keywords[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File
    Should Be Equal    ${test.keywords[1].name}    Using Test Case File User Keywords Nested
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[1]}    Using Test Case File User Keywords    Keyword Only In Test Case File

Resource File User Keyword Names In Test Case File User Keyword
    ${test} =    Check Test Case    Resource File User Keyword Names In Test Case File User Keyword
    Check Name and Three Keyword Names    ${test.keywords[0]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1
    Should Be Equal    ${test.keywords[1].name}    Using Resource File User Keywords Nested
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[0]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[1]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1

Base Keyword Names In Test Case File User Keyword
    ${test} =    Check Test Case    Base Keyword Names In Test Case File User Keyword
    Check Name and Three Keyword Names    ${test.keywords[0]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1
    Should Be Equal    ${test.keywords[1].name}    Using Base Keywords Nested
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[0]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1
    Check Name and Three Keyword Names    ${test.keywords[1].keywords[1]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1

Test Case File User Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Test Case File User Keyword Names In Resource File User Keyword
    Should Be Equal    ${test.keywords[0].name}    my_resource_1.Using Test Case File User Keywords In Resource
    Check Name and Three Keyword Names    ${test.keywords[0].keywords[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File

Resource File User Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Resource File User Keyword Names In Resource File User Keyword
    Check Name and Three Keyword Names    ${test.keywords[0]}    my_resource_1.Using Resource File User Keywords In Resource 1    my_resource_1.Keyword Only In Resource 1
    Check Name and Three Keyword Names    ${test.keywords[1]}    my_resource_1.Using Resource File User Keywords In Resource 2    my_resource_2.Keyword Only In Resource 2

Base Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Base Keyword Names In Resource File User Keyword
    Check Name and Three Keyword Names    ${test.keywords[0]}    my_resource_1.Using Base Keywords In Resource    MyLibrary1.Keyword Only In Library 1

User Keyword Name Containing Dots
    Check Test And Three Keyword Names    User Keyword Name Containing Dots    User Keyword.Name

User Keyword Name Ending With Dot
    Check Test And Three Keyword Names    User Keyword Name Ending With Dot    User Keyword.

Name Set Using 'robot_name' Attribute
    Check Test Case  ${TESTNAME}

Old Name Doesn't Work If Name Set Using 'robot_name'
    Check Test Case  ${TESTNAME}

*** Keywords ***
Check Test And Three Keyword Names
    [Arguments]    ${test_name}    ${exp_kw_name}
    ${test} =    Check Test Case    ${test_name}
    Check Three Keyword Names    ${test}    ${exp_kw_name}

Check Name And Three Keyword Names
    [Arguments]    ${item}    ${exp_name}    ${exp_kw_name}
    Should Be Equal    ${item.name}    ${exp_name}
    Check Three Keyword Names    ${item}    ${exp_kw_name}

Check Three Keyword Names
    [Arguments]    ${item}    ${exp_kw_name}
    Should Be Equal    ${item.keywords[0].name}    ${exp_kw_name}
    Should Be Equal    ${item.keywords[1].name}    ${exp_kw_name}
    Should Be Equal    ${item.keywords[2].name}    ${exp_kw_name}
