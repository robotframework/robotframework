*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/deprecated_builtin/grep.robot
Resource        atest_resource.robot

*** Test Cases ***
Grep Literal
    Check Test Case  Grep Literal

Grep Case Insensitive
    Check Test Case  Grep Case Insensitive

Grep Simple Pattern
    Check Test Case  Grep Simple Pattern

Grep Regexp
    Check Test Case  Grep Regexp

Grep Is Deprecated
    Length Should Be  ${ERRORS.msgs}  18
    :FOR    ${error}    IN    @{ERRORS}
    \    Check Log Message    ${error}
    ...    Keyword 'DeprecatedBuiltIn.Grep' is deprecated. Use 'String.Get Lines Containing/Matching' keywords instead.
    ...    WARN
