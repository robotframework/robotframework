*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    tags/-tag_syntax.robot
Resource          atest_resource.robot

*** Test Cases ***
Deprecation warning with test
    Check Test Tags    Deprecation warning    -literal-with-force    -warn-with-test
    Check Deprecation Warning    0    tags/-tag_syntax.robot    11    -warn-with-test

Deprecation warning with keyword
    ${tc} =    Check Test Case    Deprecation warning
    Check Keyword Data    ${tc.kws[0]}    Keyword    tags=-warn-with-keyword
    Check Deprecation Warning    1    tags/-tag_syntax.robot    25    -warn-with-keyword

Deprecation warning with keyword in resource
    ${tc} =    Check Test Case    Deprecation warning
    Check Keyword Data    ${tc.kws[1]}    -tag_syntax.Keyword In Resource    tags=-warn-with-keyword-in-resource
    Check Deprecation Warning    2    tags/-tag_syntax.resource    3    -warn-with-keyword-in-resource

No deprecation warning from Settings, when escaped, or with variables
    Length Should Be    ${ERRORS}    3

Escaped
    Check Test Tags    ${TESTNAME}    -literal-escaped    -literal-with-force

Variable
    Check Test Tags    ${TESTNAME}    -literal-with-force    -literal-with-variable

*** Keywords ***
Check Deprecation Warning
    [Arguments]    ${index}    ${source}    ${lineno}    ${tag}
    Error in file    ${index}    ${source}    ${lineno}
    ...    Settings tags starting with a hyphen using the '[Tags]' setting is deprecated.
    ...    In Robot Framework 7.0 this syntax will be used for removing tags.
    ...    Escape '${tag}' like '\\${tag}' to use the literal value and to avoid this warning.
    ...    level=WARN    pattern=False
