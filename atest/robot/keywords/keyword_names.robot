*** Settings ***
Documentation     Tests for how keyword names are logged in outputs. Should
...               always use full names (e.g. 'MyLib.My Keyword') and use format
...               defined in library or resource, not format that is used.
Suite Setup       Run Tests    --pythonpath ${RESDIR}    keywords/keyword_names.robot
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
    Check Name and Three Keyword Names    ${test.body[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File
    Should Be Equal    ${test.body[1].name}    Using Test Case File User Keywords Nested
    Check Name and Three Keyword Names    ${test.body[1].body[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File
    Check Name and Three Keyword Names    ${test.body[1].body[1]}    Using Test Case File User Keywords    Keyword Only In Test Case File

Resource File User Keyword Names In Test Case File User Keyword
    ${test} =    Check Test Case    Resource File User Keyword Names In Test Case File User Keyword
    Check Name and Three Keyword Names    ${test.body[0]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1
    Should Be Equal    ${test.body[1].name}    Using Resource File User Keywords Nested
    Check Name and Three Keyword Names    ${test.body[1].body[0]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1
    Check Name and Three Keyword Names    ${test.body[1].body[1]}    Using Resource File User Keywords    my_resource_1.Keyword Only In Resource 1

Base Keyword Names In Test Case File User Keyword
    ${test} =    Check Test Case    Base Keyword Names In Test Case File User Keyword
    Check Name and Three Keyword Names    ${test.body[0]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1
    Should Be Equal    ${test.body[1].name}    Using Base Keywords Nested
    Check Name and Three Keyword Names    ${test.body[1].body[0]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1
    Check Name and Three Keyword Names    ${test.body[1].body[1]}    Using Base Keywords    MyLibrary1.Keyword Only In Library 1

Test Case File User Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Test Case File User Keyword Names In Resource File User Keyword
    Should Be Equal    ${test.body[0].name}    my_resource_1.Using Test Case File User Keywords In Resource
    Check Name and Three Keyword Names    ${test.body[0].body[0]}    Using Test Case File User Keywords    Keyword Only In Test Case File

Resource File User Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Resource File User Keyword Names In Resource File User Keyword
    Check Name and Three Keyword Names    ${test.body[0]}    my_resource_1.Using Resource File User Keywords In Resource 1    my_resource_1.Keyword Only In Resource 1
    Check Name and Three Keyword Names    ${test.body[1]}    my_resource_1.Using Resource File User Keywords In Resource 2    my_resource_2.Keyword Only In Resource 2

Base Keyword Names In Resource File User Keyword
    ${test} =    Check Test Case    Base Keyword Names In Resource File User Keyword
    Check Name and Three Keyword Names    ${test.body[0]}    my_resource_1.Using Base Keywords In Resource    MyLibrary1.Keyword Only In Library 1

User Keyword Name Containing Dots
    Check Test And Three Keyword Names    User Keyword Name Containing Dots    User Keyword.Name

User Keyword Name Ending With Dot
    Check Test And Three Keyword Names    User Keyword Name Ending With Dot    User Keyword.

Name Set Using 'robot_name' Attribute
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    MyLibrary1.Name set using 'robot_name' attribute
    Check Log Message    ${tc.kws[0].msgs[0]}    My name was set using 'robot_name' attribute!

Name Set Using 'robot.api.deco.keyword' Decorator
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    MyLibrary1.Name set using 'robot.api.deco.keyword' decorator
    Check Log Message    ${tc.kws[0].msgs[0]}    My name was set using 'robot.api.deco.keyword' decorator!

Custom non-ASCII name
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    MyLibrary1.Custom nön-ÄSCII name

Old Name Doesn't Work If Name Set Using 'robot_name'
    Check Test Case    ${TESTNAME}

Keyword can just be marked without changing its name
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    MyLibrary1.No Custom Name Given 1
    Should Be Equal    ${tc.kws[1].name}    MyLibrary1.No Custom Name Given 2

Functions decorated with @keyword can start with underscrore
    ${tc} =    Check Test Case    ${TESTNAME}
    Should Be Equal    ${tc.kws[0].name}    MyLibrary1.I Start With An Underscore And I Am Ok
    Check Log Message    ${tc.kws[0].msgs[0]}    I'm marked with @keyword
    Should Be Equal    ${tc.kws[1].name}    MyLibrary1.Function name can be whatever
    Check Log Message    ${tc.kws[1].msgs[0]}    Real name set by @keyword

Assignment is not part of name
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword name and assign should be    ${tc.kws[0]}    BuiltIn.Log
    Keyword name and assign should be    ${tc.kws[1]}    BuiltIn.Set Variable    \${var}
    Keyword name and assign should be    ${tc.kws[2]}    BuiltIn.Set Variable    \${v1}    \${v2}
    Keyword name and assign should be    ${tc.kws[3]}    BuiltIn.Evaluate    \${first}    \@{rest}

Library name and keyword name are separate
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword and library names should be    ${tc.kws[0]}    Keyword Only In Test Case File
    Keyword and library names should be    ${tc.kws[1]}    Keyword Only In Resource 1    my_resource_1
    Keyword and library names should be    ${tc.kws[2]}    Keyword Only In Resource 1    my_resource_1
    Keyword and library names should be    ${tc.kws[3]}    Log    BuiltIn
    Keyword and library names should be    ${tc.kws[4]}    Log    BuiltIn

Empty keyword name is not allowed
    Error in library    MyLibrary1
    ...    Adding keyword '__' failed:
    ...    Keyword name cannot be empty.

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
    Should Be Equal    ${item.body[0].name}    ${exp_kw_name}
    Should Be Equal    ${item.body[1].name}    ${exp_kw_name}
    Should Be Equal    ${item.body[2].name}    ${exp_kw_name}

Keyword name and assign should be
    [Arguments]    ${kw}    ${name}    @{assign}
    Should Be Equal    ${kw.name}    ${name}
    Lists Should Be Equal    ${kw.assign}    ${assign}

Keyword and library names should be
    [Arguments]    ${kw}    ${kwname}    ${libname}=${None}
    Should Be Equal    ${kw.kwname}     ${kwname}
    Should Be Equal    ${kw.libname}    ${libname}
    IF    $libname is None
        Should Be Equal    ${kw.name}    ${kwname}
    ELSE
        Should Be Equal    ${kw.name}    ${libname}.${kwname}
    END
