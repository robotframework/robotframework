*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_recommendations.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Keyword From Library Not Imported
    Check Test Case    ${TESTNAME}

Implicit Keyword With Typo
    Check Test Case    ${TESTNAME}

Explicit Keyword With Typo
    Check Test Case    ${TESTNAME}

Explicit Keyword Similar To Keyword In Imported Library
    Check Test Case    ${TESTNAME}

Implicit Keyword Similar To Keyword In Imported Library
    Check Test Case    ${TESTNAME}

Explicit Keyword Similar To Keyword In Imported Resource
    Check Test Case    ${TESTNAME}

Implicit Keyword Similar To Keyword In Imported Resource
    Check Test Case    ${TESTNAME}

Implicit Long Alphanumeric Garbage Keyword
    Check Test Case    ${TESTNAME}

Explicit Long Alphanumeric Garbage Keyword
    Check Test Case    ${TESTNAME}

Implicit Special Character Garbage Keyword
    Check Test Case    ${TESTNAME}

Explicit Special Character Garbage Keyword
    Check Test Case    ${TESTNAME}

Implicit Keyword Similar To User Keyword
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword
    Check Test Case    ${TESTNAME} Implicit Missing
    Check Test Case    ${TESTNAME} Explicit Missing
    Check Test Case    ${TESTNAME} Implicit Missing Similar To Both Libraries
    Check Test Case    ${TESTNAME} Explicit Missing Similar To Both Libraries
    Check Test Case    ${TESTNAME} And Ignore Error
    Check Test Case    ${TESTNAME} Whitespace

Misspelled Keyword
    Check Test Case    ${TESTNAME} Capitalized
    Check Test Case    ${TESTNAME} Lowercase
    Check Test Case    ${TESTNAME} All Caps
    Check Test Case    ${TESTNAME} Underscore
    Check Test Case    ${TESTNAME} Explicit
    Check Test Case    ${TESTNAME} Spacing
    Check Test Case    ${TESTNAME} No Whitespace

Keyword With Period
    Check Test Case    ${TESTNAME}

Keyword With Periods
    Check Test Case    ${TESTNAME}

Similar User Keywords
    Check Test Case    ${TESTNAME}

Similar Keywords In Resources And Libraries
    Check Test Case    ${TESTNAME}

Non-similar Embedded User Keyword
    Check Test Case    ${TESTNAME}

Embedded Similar User Keywords
    Check Test Case    ${TESTNAME}

Existing Non-ASCII Keyword
    Check Test Case    ${TESTNAME}

Wrong Library Name
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} 2

BuiltIn Similar To Other BuiltIns
    Check Test Case    ${TESTNAME}

Substring of Long Keyword
    Check Test Case    ${TESTNAME}

Similar To Really Long Keyword
    Check Test Case    ${TESTNAME}

Keyword With Arguments Without Correct Spacing
    Check Test Case    ${TESTNAME}

Misspelled Keyword With Arguments
    Check Test Case    ${TESTNAME}

Just Library Name
    Check Test Case    ${TESTNAME}

Leading Period Keyword
    Check Test Case    ${TESTNAME}

Leading Period Library Name
    Check Test Case    ${TESTNAME}

Ending In Period Keyword
    Check Test Case    ${TESTNAME}

Ending In Period Library Name
    Check Test Case    ${TESTNAME}

Period
    Check Test Case    ${TESTNAME}

Underscore
    Check Test Case    ${TESTNAME}

Dollar
    Check Test Case    ${TESTNAME}

Curly Brace
    Check Test Case    ${TESTNAME}

More Non-ASCII
    Check Test Case    ${TESTNAME}

Non-ASCII But Similar
    Check Test Case    ${TESTNAME}

Explicit Many Similar Keywords
    Check Test Case    ${TESTNAME}

Implicit Many Similar Keywords
    Check Test Case    ${TESTNAME}

Explicit Substring Of Many Keywords
    Check Test Case    ${TESTNAME}

Implicit Substring Of Many Keywords
    Check Test Case    ${TESTNAME}

Excluded Library
    Check Test Case    ${TESTNAME}
