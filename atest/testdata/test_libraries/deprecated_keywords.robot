*** Settings ***
Library           DeprecatedKeywords.py

*** Test Cases ***
Deprecated keywords
    Deprecated Library Keyword
    Deprecated User Keyword

Multiline message
    Deprecated Library Keyword With Multiline Message
    Deprecated User Keyword With Multiline Message

Deprecated keywords without extra doc
    Deprecated Library Keyword Without Extra Doc
    Deprecated User Keyword Without Extra Doc

Text between `*DEPRECATED` and closing `*` is ignored
    Deprecated Library Keyword With Stuff To Ignore
    Deprecated User Keyword With Stuff To Ignore

Assignment is not included in keyword name
    ${var} =    Deprecated Keyword Returning
    Should Be Equal As Numbers    ${var}    42

Not deprecated keywords
    Not Deprecated With Doc
    Not Deprecated Without Doc
    Not Deprecated With Deprecated Prefix
    Not Deprecated User Keyword
    Not Deprecated User Keyword Without Documentation
    Not Deprecated User Keyword With `*Deprecated` Prefix

*** Keywords ***
Deprecated User Keyword
    [Documentation]    *DEPRECATED* Use keyword `Not Deprecated User Keyword` instead.
    No Operation

Deprecated User Keyword With Multiline Message
    [Documentation]    *DEPRECATED* Message in
    ...                multiple
    ...                lines.
    ...
    ...                Ignore this.
    ...                And this.
    No Operation

Deprecated User Keyword With Stuff To Ignore
    [Documentation]    *DEPRECATED Ignore this!!* Keep this!!
    No Operation

Deprecated User Keyword Without Extra Doc
    [Documentation]    *DEPRECATED*
    No Operation

Not Deprecated User Keyword
    [Documentation]    Some documentation
    No Operation

Not Deprecated User Keyword Without Documentation
    No Operation

Not Deprecated User Keyword With `*Deprecated` Prefix
    [Documentation]    *DEPRECATED ... just kidding!!
    No Operation
