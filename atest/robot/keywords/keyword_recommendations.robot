*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/keyword_recommendations.robot
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

Wrapped By Run Keyword Implicit Missing
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword Explicit Missing
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword Implicit Missing Similar To Both Libraries
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword Explicit Missing Similar To Both Libraries
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword And Ignore Error
    Check Test Case    ${TESTNAME}

Wrapped By Run Keyword Whitespace
    Check Test Case    ${TESTNAME}

Misspelled Keyword Capitalized
    Check Test Case    ${TESTNAME}

Misspelled Keyword Lowercase
    Check Test Case    ${TESTNAME}

Misspelled Keyword All Caps
    Check Test Case    ${TESTNAME}

Misspelled Keyword Underscore
    Check Test Case    ${TESTNAME}

Misspelled Keyword Explicit
    Check Test Case    ${TESTNAME}

Misspelled Keyword Spacing
    Check Test Case    ${TESTNAME}

Misspelled Keyword No Whitespace
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

Missing separator between keyword and arguments
    Check Test Case    ${TESTNAME}

Missing separator between keyword and arguments with multiple matches
    Check Test Case    ${TESTNAME}
