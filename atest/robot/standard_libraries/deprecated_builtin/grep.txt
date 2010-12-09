*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/deprecated_builtin/grep.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
Grep Literal
    Check Test Case  Grep Literal

Grep Case Insensitive
    Check Test Case  Grep Case Insensitive

Grep Simple Pattern
    Check Test Case  Grep Simple Pattern

Grep Regexp
    Check Test Case  Grep Regexp

No Deprecation Warning Is Shown When Grep Is Used
    Length Should Be  ${ERRORS.msgs}  0

Regexp Escape
    Check Test Case  Regexp Escape
