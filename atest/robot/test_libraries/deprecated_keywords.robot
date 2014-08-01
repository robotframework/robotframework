*** Setting ***
Suite Setup       Run Tests    \    test_libraries${/}deprecated_keywords.html
Force Tags        regression    pybot    jybot
Resource          atest_resource.robot

*** Variable ***

*** Test Case ***
Deprecated Library Keyword
    Verify Test and Deprecation Warnings    Deprecated Library Keyword    Keyword 'DeprecatedKeywords.Deprecated Library Keyword' is deprecated. Use keyword `Not Deprecated With Doc` instead!
    Check Syslog Does Not Contain    ignore this

Deprecated User Keyword
    Verify Test and Deprecation Warnings    Deprecated User Keyword    Keyword 'Deprecated User Keyword' is deprecated. Use keyword `Not Deprecated User Keyword` instead.

Deprecated User Keyword Without Extra Doc
    Verify Test and Deprecation Warnings    Deprecated User Keyword Without Extra Doc    Keyword 'Deprecated User Keyword Without Extra Doc' is deprecated.

Variable Names Are removed From SetKeyword Names
    Verify Test and Deprecation Warnings    Variable Names Are removed From SetKeyword Names    Keyword 'DeprecatedKeywords.Deprecated Keyword Returning' is deprecated. But still returning a value!

Not Deprecated Keywords
    Check Test Case    Not Deprecated Keywords
    Check Syslog Does Not Contain    Not Deprecated With Doc' is deprecated.    Not Deprecated Without Doc' is deprecated.    Not Deprecated User Keyword' is deprecated.    Not Deprecated User Keyword Without Documentation' is deprecated.    Comment' is deprecated.

*** Keyword ***
Verify Test and Deprecation Warnings
    [Arguments]    ${testname}    ${expmsg}
    ${tc} =    Check Test Case    ${testname}
    Check Log Message    ${tc.kws[0].msgs[0]}    ${expmsg}    WARN
    Check Syslog Contains    | WARN \ |    ${expmsg}
