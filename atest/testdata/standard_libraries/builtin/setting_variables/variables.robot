*** Setting ***
Documentation     See also variables2.html
Suite Setup       My Suite Setup
Suite Teardown    My Suite Teardown
Library           OperatingSystem
Library           Collections

*** Variable ***
@{LIST}           Hello    world
${SCALAR}         Hi tellus

*** Test Case ***
Set Variable
    ${var} =    Set Variable    Hello
    Should Be Equal    ${var}    Hello
    @{mylist1} =    Set Variable    ${LIST}
    ${mylist2} =    Set Variable    ${LIST}
    Should Be Equal    ${mylist1}    ${LIST}
    Should Be Equal    ${mylist2}    ${LIST}

Set Variable With More Or Less Than One Value
    ${var1}    ${var2} =    Set Variable    Hello    world
    Should Be Equal    ${var1}+${var2}    Hello+world
    @{mylist} =    Set Variable    Hi    again
    Should Be Equal    @{mylist}[0]+@{mylist}[1]    Hi+again
    ${scal} =    Set Variable    Hello    world
    Should Be Equal    ${scal}    ${LIST}
    ${emp} =    Set Variable
    Should Be Equal    ${emp}    ${EMPTY}

Set Test Variable - Scalars
    [Documentation]    FAIL Non-existing variable '\${non_existing}'.
    Should Be Equal    ${scalar}    Hi tellus
    Set Test Variable    $scalar    Hello    world
    Should Be True    ${scalar} == ['Hello', 'world']    Hello world
    ${scalar} =    Set    Moi maailma
    Set Test Variable    \${scalar}
    Should Be Equal    ${scalar}    Moi maailma
    Set Test Variable    $new    Previously non-existing
    Should Be Equal    ${new}    Previously non-existing
    Set Test Variable    $non_existing

Set Test Variable - Lists
    Should Be True    @{list} == ['Hello', 'world']
    Set Test Variable    \@{list}    One item
    Should Be True    @{list} == ['One item']
    Set Test Variable    @list    One    Two    Three
    Should Be True    @{list} == ['One','Two','Three']
    @{list} =    Set Variable    1    2    3
    Set Test Variable    @{list}
    Should Be True    @{list} == ['1','2','3']
    Set Test Variable    @new    This    is    ok
    Should Be True    @{new} == ['This','is','ok']

Set Test Variable Needing Escaping
    Set Test Variable    $var1    One backslash \\ and \${notvar}
    Should Be Equal    ${var1}    One backslash \\ and \${notvar}
    ${var2} =    Set    \ \\ \\\ \\\\ \\\\\ \\\\\\
    Should Be Equal    ${var2}    \ \\ \\\ \\\\ \\\\\ \\\\\\    Sanity check
    Set Test Variable    $var2
    Should Be Equal    ${var2}    \ \\ \\\ \\\\ \\\\\ \\\\\\
    ${var3} =    Set    \    \\    \\\
    Should Be True    ${var3} == ['', '\\\\', '\\\\']
    Set Test Variable    $var3
    Should Be True    ${var3} == ['', '\\\\', '\\\\']
    Should Be Equal    ${var3[0]}    ${EMPTY}
    Should Be Equal    ${var3[1]}    \\
    Should Be Equal    ${var3[2]}    \\
    @{var4} =    List    \    \\    \\\
    Set Test Variable    @var4
    Should Be Equal    @{var4}[0]    ${EMPTY}
    Should Be Equal    @{var4}[1]    \\
    Should Be Equal    @{var4}[2]    \\
    Set Test Variable    @var5    \\    \\\    \\\\
    Should Be Equal    @{var5}[0]    \\
    Should Be Equal    @{var5}[1]    \\
    Should Be Equal    @{var5}[2]    \\\\

Set Test Variable In User Keyword
    ${new_var} =    Set    Value of new var
    Variable Should Not Exist    $uk_var_1
    Variable Should Not Exist    $uk_var_2
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    $uk_var_4
    Set Test Variables In UK
    Should Be Equal    ${uk_var_1}    Value of uk var 1
    Should Be Equal    ${uk_var_2}    Value of uk var 2
    Should Be True    @{uk_var_3} == ['Value of', 'uk var 3']
    Variable Should Not Exist    $uk_var_4
    Check Test Variables Available In UK

Set Test Variable Not Affecting Other Tests
    Should Be Equal    ${scalar}    Hi tellus
    Should Be True    @{list} == ['Hello', 'world']
    Variable Should Not Exist    $new_var
    Variable Should Not Exist    $uk_var_1
    Variable Should Not Exist    $uk_var_2
    Variable Should Not Exist    @uk_var_3
    Variable Should Not Exist    $uk_var_4
    Check Test Variables Not Available In UK

Set Suite Variable 1
    [Documentation]    FAIL Non-existing variable '\${non_existing}'.
    Variable Should Not Exist    $parent_suite_setup_suite_var
    Set Suite Variable    $parent_suite_setup_suite_var    Parent should not see this value
    Variable Should Not Exist    $suite_setup_local_var
    Should Be Equal    ${suite_setup_suite_var}    Suite var set in suite setup
    Should Be True    @{suite_setup_suite_var} == [ 'Suite var set in', 'suite setup' ]
    Set Suite Variable    $test_level_suite_var    Suite var set in test
    @{test_level_suite_var} =    Create List    Suite var set in    test
    Set Suite Variable    @test_level_suite_var
    Set Suite Variable    $suite_var_needing_escaping    One backslash \\ and \${notvar}
    Should Be Equal    ${test_level_suite_var}    Suite var set in test
    Should Be True    @{test_level_suite_var} == [ 'Suite var set in', 'test' ]
    Should Be Equal    ${suite_var_needing_escaping}    One backslash \\ and \${notvar}
    Set Suite Variables In UK
    Should Be Equal    ${uk_level_suite_var}    Suite var set in user keyword
    Should Be True    @{uk_level_suite_var} == [ 'Suite var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be True    @{sub_uk_level_suite_var} == [ 'Suite var set in', 'sub user keyword' ]
    Check Suite Variables Available In UK
    Set Suite Variable    \${non_existing}

Set Suite Variable 2
    [Documentation]    FAIL Invalid variable syntax 'invalid'
    Should Be Equal    ${test_level_suite_var}    Suite var set in test
    Should Be True    @{test_level_suite_var} == [ 'Suite var set in', 'test' ]
    Should Be Equal    ${suite_var_needing_escaping}    One backslash \\ and \${notvar}
    Should Be Equal    ${uk_level_suite_var}    Suite var set in user keyword
    Should Be True    @{uk_level_suite_var} == [ 'Suite var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be True    @{sub_uk_level_suite_var} == [ 'Suite var set in', 'sub user keyword' ]
    Check Suite Variables Available In UK
    Set Suite Variable    invalid

Set Global Variable 1
    [Documentation]    FAIL Non-existing variable '\@{non_existing}'.
    Should Be Equal    ${parent_suite_setup_global_var}    Set in __init__
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be True    @{suite_setup_global_var} == [ 'Global var set in', 'suite setup' ]
    Set Global Variable    $test_level_global_var    Global var set in test
    @{test_level_global_var} =    Create List    Global var set in    test
    Set Global Variable    @test_level_global_var
    Set Global Variable    $global_var_needing_escaping    Four backslashes \\\\\\\\ and \\\${notvar}
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be True    @{test_level_global_var} == [ 'Global var set in', 'test' ]
    Should Be Equal    ${global_var_needing_escaping}    Four backslashes \\\\\\\\ and \\\${notvar}
    Set Global Variables In UK
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be True    @{uk_level_global_var} == [ 'Global var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be True    @{sub_uk_level_global_var} == [ 'Global var set in', 'sub user keyword' ]
    Check Global Variables Available In UK
    Set Global Variable    @non_existing

Set Global Variable 2
    [Documentation]    FAIL Invalid variable syntax 'invalid syntax'
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be True    @{test_level_global_var} == [ 'Global var set in', 'test' ]
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be True    @{uk_level_global_var} == [ 'Global var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be True    @{sub_uk_level_global_var} == [ 'Global var set in', 'sub user keyword' ]
    Check Global Variables Available In UK
    Set Global Variable    invalid syntax

Set Test/Suite/Global Variables With Normal Variable Syntax 1
    Set Test Variable    ${new test var 1}    test
    Set Suite Variable    @{new suite var 1}    suite    variable
    Set Global Variable    @{new global var 1}    global with \ escapes \\    /home/peke/Devel/robotframework/atest/testdata/standard_libraries/builtin/setting_variables ${TEMPDIR} \${escaped and not a var}
    Should Be Equal    ${new test var 1}    test
    Should Be True    @{new suite var 1} == 'suite variable'.split()
    Should Be Equal    @{new global var 1}[0]    global with \ escapes \\
    Should Be Equal    @{new global var 1}[1]    /home/peke/Devel/robotframework/atest/testdata/standard_libraries/builtin/setting_variables ${TEMPDIR} \${escaped and not a var}

Set Test/Suite/Global Variables With Normal Variable Syntax 2
    Should Be True    @{new suite var 1} == 'suite variable'.split()
    Should Be Equal    @{new global var 1}[0]    global with \ escapes \\
    Should Be Equal    @{new global var 1}[1]    /home/peke/Devel/robotframework/atest/testdata/standard_libraries/builtin/setting_variables ${TEMPDIR} \${escaped and not a var}

It Should Be Possible To Set Test/Suite/Global Variable Using Empty List Variable 1
    @{empty} =    Create List
    Set Test Variable    ${new test var 2}    @{empty}
    Set Suite Variable    @{new suite var 2}    @{empty}
    Set Global Variable    ${new global var 2}    @{empty}
    Should Be True    ${new test var 2} == []
    Should Be True    @{new suite var 2} == []
    Should Be True    ${new global var 2} == []

It Should Be Possible To Set Test/Suite/Global Variable Using Empty List Variable 2
    Should Be True    @{new suite var 2} == []
    Should Be True    ${new global var 2} == []

Scopes And Overriding 1
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    CLI2
    Should Be Equal    ${cli_var_3}    CLI3
    Set Test Variable    $cli_var_1    New value 1
    Set Suite Variable    $cli_var_2    New value 2
    Set Global Variable    $cli_var_3    New value 3
    Set Global Variable    $parent_suite_setup_global_var_to_reset    Set in test!
    Should Be Equal    ${cli_var_1}    New value 1
    Should Be Equal    ${cli_var_2}    New value 2
    Should Be Equal    ${cli_var_3}    New value 3
    Should Be Equal    ${parent_suite_setup_global_var_to_reset}    Set in test!

Scopes And Overriding 2
    Should Be Equal    ${cli_var_1}    CLI1
    Should Be Equal    ${cli_var_2}    New value 2
    Should Be Equal    ${cli_var_3}    New value 3

Overiding Variable When It Has Non-string Value
    ${v1} =    Set Variable    ${1}
    ${v2} =    Create List    a    b
    Set Test Variable    ${v1}    a string
    Set Global Variable    ${v2}    ${42}
    Should Be Equal    ${v1} - ${v2}    a string - 42

Set Test/Suite/Global Variable In User Keyword When Variable Name Is Used As Argument
    : FOR    ${type}    IN    Test    Suite    Global
    \    Test Setting Variable In User Keyword    \${variable}    ${type}
    \    Test Setting Variable In User Keyword    $variable    ${type}

Setting Test/Suite/Global Variable Which Value Is In Variable Like Syntax
    Set Test Variable    ${variable}    \\\${foo}
    Set Test Variable    \${variable}    bar
    Should Be Equal    ${variable}    bar
    ${foo} =    Set Variable    value
    Set Suite Variable    ${variable}    \\\${foo}
    Set Suite Variable    \${variable}    bar
    Should Be Equal    ${variable}    bar

Setting Test/Suite/Global Variable Which Value Is In Variable Syntax
    Set Test Variable    ${variable}    \${foo}
    Set Test Variable    \${variable}    bar
    Should Be Equal    ${variable}    bar
    ${foo} =    Set Variable    value
    Set Suite Variable    ${variable}    \${foo}
    Set Suite Variable    \${variable}    bar
    Should Be Equal    ${variable}    bar

Set Test/Suite/Global Variable With Internal Variables In Name
    [Documentation]    This obscure test is here to prevent this bug from reappearing:\n http://code.google.com/p/robotframework/issues/detail?id=397\n FAIL Non-existing variable '\${nonex}'.
    ${x} =    Set Variable    bar
    Set Test Variable    \${foo ${x}}    value
    Should Be Equal    ${foo bar}    value
    Set Suite Variable    ${${x}${x[:-1]}ari}    conan
    Should Be Equal    ${barbaari}    conan
    Set Global Variable    $${x}    pub
    Should Be Equal    ${bar}    pub
    Set Test Variable    ${xxx ${nonex}}    whatever

Using @{EMPTY} to with `Set Test/Suite/Global Variable` keywords
    Set Test Variable    @{LIST}    @{EMPTY}
    Should Be Empty    ${LIST}
    Append To List    ${LIST}    test
    Should Be True    ${LIST} == ['test']
    Verify @{EMPTY} is still empty
    Set Suite Variable    @{LIST}    @{EMPTY}
    Should Be Empty    ${LIST}
    Append To List    ${LIST}    suite
    Verify @{EMPTY} is still empty
    Set Global Variable    @{NEW}    @{EMPTY}
    Should Be Empty    ${NEW}
    Append To List    ${NEW}    global
    Verify @{EMPTY} is still empty

Using @{EMPTY} to with `Set Test/Suite/Global Variable` keywords 2
    Should Be True    ${LIST} == ['suite']
    Should Be True    ${NEW} == ['global']


*** Keyword ***
My Suite Setup
    ${suite_setup_local_var} =    Set Variable    Variable available only locally    in suite setup
    Set Suite Variable    $suite_setup_suite_var    Suite var set in suite setup
    @{suite_setup_suite_var} =    Create List    Suite var set in    suite setup
    Set Suite Variable    @suite_setup_suite_var
    ${suite_setup_global_var} =    Set Variable    Global var set in suite setup
    Set Global Variable    $suite_setup_global_var
    Set Global Variable    @suite_setup_global_var    Global var set in    suite setup
    Should Be True    ${suite_setup_local_var} == [ 'Variable available only locally', 'in suite setup' ]
    Should Be Equal    ${suite_setup_suite_var}    Suite var set in suite setup
    Should Be True    @{suite_setup_suite_var} == [ 'Suite var set in', 'suite setup' ]
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be True    @{suite_setup_global_var} == [ 'Global var set in', 'suite setup' ]
    Variable Should Not Exist    $parent_suite_setup_suite_var
    Should Be Equal    ${parent_suite_setup_global_var}    Set in __init__

My Suite Teardown
    Set Suite Variable    $suite_teardown_suite_var    Suite var set in suite teardown
    Should Be Equal    ${suite_setup_suite_var}    Suite var set in suite setup
    Should Be Equal    ${test_level_suite_var}    Suite var set in test
    Should Be Equal    ${uk_level_suite_var}    Suite var set in user keyword
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be Equal    ${suite_teardown_suite_var}    Suite var set in suite teardown
    Set Global Variable    $suite_teardown_global_var    Global var set in suite teardown
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be Equal    ${suite_teardown_global_var}    Global var set in suite teardown
    Check Suite Variables Available In UK
    Check Global Variables Available In UK

Set Test Variables In UK
    Should Be Equal    ${scalar}    Hi tellus
    Should Be Equal    ${new_var}    Value of new var
    Set Test Variable    \${uk_var_1}    Value of uk var 1
    ${uk_var_2} =    Set    Value of uk var 2
    Set Test Variable    $uk_var_2
    Set Test Variable    @uk_var_3    Value of    uk var 3
    ${uk_var_4} =    Set    This is a private variable for this user keyword

Check Test Variables Available In UK
    Should Be Equal    ${scalar}    Hi tellus
    Should Be Equal    ${new_var}    Value of new var
    Should Be Equal    ${uk_var_1}    Value of uk var 1
    Should Be Equal    ${uk_var_2}    Value of uk var 2
    Should Be True    @{uk_var_3} == ['Value of', 'uk var 3']
    Fail If Variable Exists    $uk_var_4

Check Test Variables Not Available In UK
    Equals    ${scalar}    Hi tellus
    Should Be True    @{list} == ['Hello', 'world']
    Fail If Variable Exists    $new_var
    Fail If Variable Exists    $uk_var_1
    Fail If Variable Exists    $uk_var_2
    Fail If Variable Exists    @uk_var_3
    Fail If Variable Exists    $uk_var_4

Set Suite Variables In UK
    ${uk_level_suite_var} =    String    Suite var set in user keyword
    Set Suite Variable    \${uk_level_suite_var}
    Set Suite Variable    \@{uk_level_suite_var}    Suite var set in    user keyword
    Should Be Equal    ${uk_level_suite_var}    Suite var set in user keyword
    Should Be True    @{uk_level_suite_var} == [ 'Suite var set in', 'user keyword' ]
    Set Suite Variables In Sub UK
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be True    @{sub_uk_level_suite_var} == [ 'Suite var set in', 'sub user keyword' ]

Set Suite Variables In Sub UK
    Set Suite Variable    \${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Set Suite Variable    \@{sub_uk_level_suite_var}    Suite var set in    sub user keyword
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be True    @{sub_uk_level_suite_var} == [ 'Suite var set in', 'sub user keyword' ]

Check Suite Variables Available In UK
    Fail If Variable Exists    $suite_setup_local_var
    Should Be Equal    ${suite_setup_suite_var}    Suite var set in suite setup
    Should Be True    @{suite_setup_suite_var} == [ 'Suite var set in', 'suite setup' ]
    Should Be Equal    ${test_level_suite_var}    Suite var set in test
    Should Be True    @{test_level_suite_var} == [ 'Suite var set in', 'test' ]
    Should Be Equal    ${suite_var_needing_escaping}    One backslash \\ and \${notvar}
    Should Be Equal    ${uk_level_suite_var}    Suite var set in user keyword
    Should Be True    @{uk_level_suite_var} == [ 'Suite var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_suite_var}    Suite var set in sub user keyword
    Should Be True    @{sub_uk_level_suite_var} == [ 'Suite var set in', 'sub user keyword' ]

Set Global Variables In UK
    ${uk_level_global_var} =    String    Global var set in user keyword
    Set Global Variable    \${uk_level_global_var}
    Set Global Variable    \@{uk_level_global_var}    Global var set in    user keyword
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be True    @{uk_level_global_var} == [ 'Global var set in', 'user keyword' ]
    Set Global Variables In Sub UK
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be True    @{sub_uk_level_global_var} == [ 'Global var set in', 'sub user keyword' ]

Set Global Variables In Sub UK
    Set Global Variable    \${sub_uk_level_global_var}    Global var set in sub user keyword
    Set Global Variable    \@{sub_uk_level_global_var}    Global var set in    sub user keyword
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be True    @{sub_uk_level_global_var} == [ 'Global var set in', 'sub user keyword' ]

Check Global Variables Available In UK
    Should Be Equal    ${suite_setup_global_var}    Global var set in suite setup
    Should Be True    @{suite_setup_global_var} == [ 'Global var set in', 'suite setup' ]
    Should Be Equal    ${test_level_global_var}    Global var set in test
    Should Be True    @{test_level_global_var} == [ 'Global var set in', 'test' ]
    Should Be Equal    ${global_var_needing_escaping}    Four backslashes \\\\\\\\ and \\\${notvar}
    Should Be Equal    ${uk_level_global_var}    Global var set in user keyword
    Should Be True    @{uk_level_global_var} == [ 'Global var set in', 'user keyword' ]
    Should Be Equal    ${sub_uk_level_global_var}    Global var set in sub user keyword
    Should Be True    @{sub_uk_level_global_var} == [ 'Global var set in', 'sub user keyword' ]

Test Setting Variable In User Keyword
    [Arguments]    ${arg}    ${type}
    Run Keyword    Set ${type} Variable    ${arg}    value
    Should Not Be Equal    ${arg}    value    Value is set to variable \${arg} even it should be set to variable \${variable}    False
    Should Be Equal    ${variable}    value    Value is not set to variable \${variable} even it should

Verify @{EMPTY} is still empty
    No Operation    @{EMPTY}
