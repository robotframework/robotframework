*** Setting ***
Library           DeprecatedKeywords.py

*** Test Case ***
Deprecated Library Keyword
    Deprecated Library Keyword

Deprecated User Keyword
    Deprecated User Keyword

Deprecated User Keyword Without Extra Doc
    Deprecated User Keyword Without Extra Doc

Variable Names Are removed From SetKeyword Names
    ${var} =    Deprecated Keyword Returning
    Should Be Equal As Numbers    ${var}    42

Not Deprecated Keywords
    Not Deprecated With Doc
    Not Deprecated Without Doc
    Not Deprecated User Keyword
    Not Deprecated User Keyword Without Documentation

*** Keyword ***
Deprecated User Keyword
    [Documentation]    *DEPRECATED* Use keyword `Not Deprecated User Keyword` instead.
    ...    ignore this
    Comment

Deprecated User Keyword Without Extra Doc
    [Documentation]    *DEPRECATED*
    Comment

Not Deprecated User Keyword
    [Documentation]    Some documentation
    Comment

Not Deprecated User Keyword Without Documentation
    Comment
