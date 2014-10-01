*** Setting ***
Documentation     These tests are somewhat related to variable_priorities.html tests

*** Test Case ***
Variables Set In Test Case Are Seen By User Keywords
    [Documentation]    FAIL Recursion limit exceeded
    ${test_var} =    Set Variable    Variable in test level
    Set Variable In UK
    Variable Should Not Exist    $uk_var    Variable set in uk must not be visible in test level
    Check UK Var Does Not Exists In Another UK
    Check Test Var Exists in UK Recursively

Variables Set In One Test Are Not Visible In Another
    Variable Should Not Exist    $test_var    Variable set in one test must not be visible in another

Variables Set In User Keyword Are Seen Only By Lower Level User Keywords
    ${var} =    Set Variable    Variable in test level
    Check Overriding Var In UK
    Should Be Equal    ${var}    Variable in test level    Overridden value must not be visible in test level

*** Keyword ***
Set Variable In UK
    ${uk_var} =    Set Variable    Variable in user keyword level

Check UK Var Does Not Exists In Another UK
    Variable Should Not Exist    $uk_var

Check Test Var Exists in UK Recursively
    [Arguments]    ${recursion_level}=${10}
    Should Be Equal    ${test_var}    Variable in test level
    Should Not Be Equal As Integers    ${recursion_level}    0    Recursion limit exceeded    No values
    Check Test Var Exists in UK Recursively    ${recursion_level - 1}

Check Overriding Var In UK
    Should Be Equal    ${var}    Variable in test level
    ${var} =    Set Variable    Variable overridden in uk
    Should Be Equal    ${var}    Variable overridden in uk    It must be possible to override the value set in test level
    Check Overriding Var In UK 2    Override again with this value
    Should Be Equal    ${var}    Variable overridden in uk    Value overridden again in sub keywords must not be visible to the calling keyword
    Check Overriding Var In UK 2    And once more with this
    Should Be Equal    ${var}    Variable overridden in uk    Value overridden again in sub keywords must not be visible to the calling keyword

Check Overriding Var In UK 2
    [Arguments]    ${new_value}
    Should Be Equal    ${var}    Variable overridden in uk
    Check Overriding Var In UK 3    Variable overridden in uk
    ${var} =    Set Variable    ${new_value}
    Should Be Equal    ${var}    ${new_value}
    Check Overriding Var In UK 3    ${new_value}

Check Overriding Var In UK 3
    [Arguments]    ${expected_value}
    Should Be Equal    ${var}    ${expected_value}
