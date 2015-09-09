*** Setting ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/deprecated_builtin/verify.robot
Force Tags        regression
Resource          atest_resource.robot

*** Test Case ***
Deprecated BuiltIn Should Be Imported Automatically
    Check Syslog Contains    Imported library 'DeprecatedBuiltIn' with arguments [ ] (

Keywords aliased from BuiltIn are deprecated
    Verify deprecation    2    Fail If    Should Not Be True
    Verify deprecation    -1    Matches Regexp    Should Match Regexp

Keywords only in DeprecatedBuiltIn are deprecated
    Verify deprecation    0    Error    Fail

*** Keywords ***
Verify deprecation
    [Arguments]    ${index}    ${old}    ${new}
    Check Log Message    @{ERRORS}[${index}]
    ...    Keyword 'DeprecatedBuiltIn.${old}' is deprecated. Use 'BuiltIn.${new}' instead.
    ...    WARN
