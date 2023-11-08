*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    test_libraries/deprecated_keywords.robot
Resource          atest_resource.robot

*** Test Cases ***
Deprecated keywords
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify Deprecation Warning    ${tc.kws[0]}    DeprecatedKeywords.Deprecated Library Keyword
    ...    Use keyword `Not Deprecated With Doc` instead!
    Verify Deprecation Warning    ${tc.kws[1]}    Deprecated User Keyword
    ...    Use keyword `Not Deprecated User Keyword` instead.

Multiline message
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify Deprecation Warning    ${tc.kws[0]}    DeprecatedKeywords.Deprecated Library Keyword With Multiline Message
    ...    Multiline\nmessage.
    Verify Deprecation Warning    ${tc.kws[1]}    Deprecated User Keyword With Multiline Message
    ...    Message in\nmultiple\nlines.
    Syslog Should Not Contain    Ignore this
    Syslog Should Not Contain    ignore this

Deprecated keywords without extra doc
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify Deprecation Warning    ${tc.kws[0]}    DeprecatedKeywords.Deprecated Library Keyword Without Extra Doc
    Verify Deprecation Warning    ${tc.kws[1]}    Deprecated User Keyword Without Extra Doc

Text between `*DEPRECATED` and closing `*` is ignored
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify Deprecation Warning    ${tc.kws[0]}    DeprecatedKeywords.Deprecated Library Keyword With Stuff To Ignore
    Verify Deprecation Warning    ${tc.kws[1]}    Deprecated User Keyword With Stuff To Ignore    Keep this!!

Assignment is not included in keyword name
    ${tc} =    Check Test Case    ${TESTNAME}
    Verify Deprecation Warning    ${tc.kws[0]}    DeprecatedKeywords.Deprecated Keyword Returning    But still returning a value!

Not Deprecated Keywords
    Check Test Case    Not Deprecated Keywords
    FOR    ${name}    IN
    ...    Not Deprecated With Doc
    ...    Not Deprecated Without Doc
    ...    Not Deprecated With Deprecated Prefix
    ...    Not Deprecated User Keyword
    ...    Not Deprecated User Keyword Without Documentation
    ...    Not Deprecated User Keyword With `*Deprecated` Prefix
        Syslog Should Not Contain    ${name}' is deprecated
    END

*** Keywords ***
Verify Deprecation Warning
    [Arguments]    ${kw}    ${name}    @{extra}
    ${message} =    Catenate    Keyword '${name}' is deprecated.    @{extra}
    Check Log Message    ${kw.msgs[0]}    ${message}    WARN
    Syslog Should Contain    | WARN \ |    ${message}
