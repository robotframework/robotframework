*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    tags/-tag_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Remove from test
    Check Test Tags    ${TEST NAME}    tag1    tag3    tag4

Remove from test using pattern
    Check Test Tags    ${TEST NAME}    -in-settings    tag    tag3

Remove from test using operator
    Check Test Tags    ${TEST NAME}    tag1    tag3

Deprecated operator usage in test
    Check Test Tags    ${TEST NAME}    tag1    tag3
    VAR    ${error}
    ...    Problems when removing tags using '-tag' syntax:
    ...    The behavior of tag pattern 'NOTTAG1ORT*3' will change in Robot Framework 8.0:
    ...    'NOT' is currently considered to be a Boolean operator, but in the future
    ...    operators must be surrounded with spaces or tag names must be lower case.
    Check Log Message    ${ERRORS[1]}    ${error}    WARN

Remove from keyword
    ${tc} =    Check Test Case    Remove from test
    Check Keyword Data    ${tc[0]}    ${TEST NAME}    tags=-in-settings, kw2

Remove from keyword using documentation
    ${tc} =    Check Test Case    Remove from test
    Check Keyword Data    ${tc[1]}    ${TEST NAME}    tags=-escaped, -in-settings, -variable, kw2, kw3

Remove from keyword using pattern
    ${tc} =    Check Test Case    Remove from test using pattern
    Check Keyword Data    ${tc[0]}    -tag_syntax.${TEST NAME}    tags=r1, r5, r6

Remove from keyword using operator
    ${tc} =    Check Test Case    Remove from test using operator
    Check Keyword Data    ${tc[0]}    -tag_syntax.${TEST NAME}    tags=r1

Deprecated operator usage in keyword
    ${tc} =    Check Test Case    Deprecated operator usage in test
    Check Keyword Data    ${tc[0]}    -tag_syntax.${TEST NAME}    tags=r1
    VAR    ${error}
    ...    Problems when removing tags using '-tag' syntax:
    ...    The behavior of tag pattern 'NOTR1ORnonex' will change in Robot Framework 8.0:
    ...    'NOT' is currently considered to be a Boolean operator, but in the future
    ...    operators must be surrounded with spaces or tag names must be lower case.
    Check Log Message    ${ERRORS[2]}    ${error}    WARN

Escaped
    Check Test Tags    ${TESTNAME}    -escaped    -escaped-in-settings    -in-settings    tag    tag1    tag2    tag3

Variable
    Check Test Tags    ${TESTNAME}    -escaped-in-settings    -in-settings    -variable    tag    tag1    tag2    tag3

-tag syntax in Test Tags is deprecated
    Error in file    0    tags/-tag_syntax.robot    2
    ...    Setting tags starting with a hyphen like '-in-settings' using the 'Test Tags'
    ...    setting is deprecated. In Robot Framework 8.0 this syntax will be used for
    ...    removing tags. Escape the tag like '\\-in-settings' to use the literal value
    ...    and to avoid this warning.
    ...    level=WARN
