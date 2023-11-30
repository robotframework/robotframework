*** Settings ***
Resource          resources/recommendation_resource_1.robot
Resource          resources/recommendation_resource_2.robot
Library           resources/RecLibrary1.py
Library           resources/RecLibrary2.py    WITH NAME    Rec Library 2 With Custom Name

*** Variables ***
${INDENT}    ${SPACE * 4}

*** Test Cases ***
Keyword From Library Not Imported
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary3.Keyword Only In Library 3' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Keyword Only In Library 1
    RecLibrary3.Keyword Only In Library 3

Implicit Keyword With Typo
    [Documentation]    FAIL
    ...    No keyword with name 'Recoord' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Record
    Recoord    log message

Explicit Keyword With Typo
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrarry1.Record' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Record
    RecLibrarry1.Record    log message

Explicit Keyword Similar To Keyword In Imported Library
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary1.Keywword Only In Library 1' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Keyword Only In Library 1
    RecLibrary1.Keywword Only In Library 1

Implicit Keyword Similar To Keyword In Imported Library
    [Documentation]    FAIL
    ...    No keyword with name 'Keywword Only In Library 1' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Keyword Only In Library 1
    ...    ${INDENT}Rec Library 2 With Custom Name.Keyword Only In Library 2
    Keywword Only In Library 1

Explicit Keyword Similar To Keyword In Imported Resource
    [Documentation]    FAIL
    ...    No keyword with name 'recommendation_resource_1.Keywword Only In Resource 1' found. Did you mean:
    ...    ${INDENT}recommendation_resource_1.Keyword Only In Resource 1
    ...    ${INDENT}recommendation_resource_2.Keyword Only In Resource 2
    ...    ${INDENT}recommendation_resource_1.Keyword In Both Resources
    ...    ${INDENT}recommendation_resource_2.Keyword In Both Resources
    recommendation_resource_1.Keywword Only In Resource 1

Implicit Keyword Similar To Keyword In Imported Resource
    [Documentation]    FAIL
    ...    No keyword with name 'Keywword Only In Resource 1' found. Did you mean:
    ...    ${INDENT}recommendation_resource_1.Keyword Only In Resource 1
    ...    ${INDENT}recommendation_resource_2.Keyword Only In Resource 2
    Keywword Only In Resource 1

Implicit Long Alphanumeric Garbage Keyword
    [Documentation]    FAIL    No keyword with name 'fhj329gh9ufhds98f3972hufd9fh839832fh9ud8h8' found.
    fhj329gh9ufhds98f3972hufd9fh839832fh9ud8h8

Explicit Long Alphanumeric Garbage Keyword
    [Documentation]    FAIL    No keyword with name 'fhj329gh9ufhds98.f3972hufd9fh839832fh9ud8h8' found.
    fhj329gh9ufhds98.f3972hufd9fh839832fh9ud8h8

Implicit Special Character Garbage Keyword
    [Documentation]    FAIL    No keyword with name '*&(&^%&%$#%#@###!@!#@$$%#%&^<">:>?:""{+' found.
    *&(&^%&%$#%#@###!@!#@$$%#%&^<">:>?:""{+

Explicit Special Character Garbage Keyword
    [Documentation]    FAIL    No keyword with name '*&(&^%&%$#.%#@###!@!#@$$%#%&^<">:>?:""{+' found.
    *&(&^%&%$#.%#@###!@!#@$$%#%&^<">:>?:""{+

Implicit Keyword Similar To User Keyword
    [Documentation]    FAIL    No keyword with name 'A Uuser Keyword' found. Did you mean:
    ...    ${INDENT}A User Keyword
    A Uuser Keyword

Wrapped By Run Keyword Implicit Missing
    [Documentation]    FAIL    No keyword with name 'missing keyword' found.
    Run Keyword    missing keyword

Wrapped By Run Keyword Implicit Missing Similar To Both Libraries
    [Documentation]    FAIL
    ...    No keyword with name 'kkeyword in both libraries' found. Did you mean:
    ...    ${INDENT}Rec Library 2 With Custom Name.Keyword In Both Libraries
    ...    ${INDENT}RecLibrary1.Keyword In Both Libraries
    Run Keyword    kkeyword in both libraries

Wrapped By Run Keyword Explicit Missing Similar To Both Libraries
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary1.kkeyword in both libraries' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Keyword In Both Libraries
    Run Keyword    RecLibrary1.kkeyword in both libraries

Wrapped By Run Keyword Explicit Missing
    [Documentation]    FAIL    No keyword with name 'RecLibrary1.missing keyword' found.
    Run Keyword    RecLibrary1.missing keyword

Wrapped By Run Keyword And Ignore Error
    ${status}    ${error} =    Run Keyword And Ignore Error    missing keyword
    Should Be Equal    ${status}    FAIL
    Should Be Equal    ${error}    No keyword with name 'missing keyword' found.

Wrapped By Run Keyword Whitespace
    [Documentation]    FAIL    No keyword with name ' ' found.
    Run Keyword    ${SPACE}

Misspelled Keyword Capitalized
    [Documentation]    FAIL
    ...    No keyword with name 'Do Atcion' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    Do Atcion

Misspelled Keyword Lowercase
    [Documentation]    FAIL
    ...    No keyword with name 'do atcion' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    do atcion

Misspelled Keyword All Caps
    [Documentation]    FAIL
    ...    No keyword with name 'DO ATCION' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    DO ATCION

Misspelled Keyword Underscore
    [Documentation]    FAIL
    ...    No keyword with name 'do_atcion' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    do_atcion

Misspelled Keyword Explicit
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary1.DoAtcion' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    ...    ${INDENT}RecLibrary1.Action
    RecLibrary1.DoAtcion

Misspelled Keyword Spacing
    [Documentation]    FAIL
    ...    No keyword with name 'd o a t c i o n' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    d o a t c i o n

Misspelled Keyword No Whitespace
    [Documentation]    FAIL
    ...    No keyword with name 'DoAtcion' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Do Action
    DoAtcion

Keyword With Periods
    [Documentation]    FAIL
    ...    No keyword with name 'Kye.word.with_periods' found. Did you mean:
    ...    ${INDENT}Key.word.with periods.
    Kye.word.with_periods

Similar User Keywords
    [Documentation]    FAIL
    ...    No keyword with name 'Similar User Keyword 4' found. Did you mean:
    ...    ${INDENT}Similar User Keyword 3
    ...    ${INDENT}Similar User Keyword 2
    ...    ${INDENT}Similar User Keyword 1
    Similar User Keyword 4

Similar Keywords In Resources And Libraries
    [Documentation]    FAIL
    ...    No keyword with name 'Similar Kw' found. Did you mean:
    ...    ${INDENT}Similar Kw 5
    ...    ${INDENT}Rec Library 2 With Custom Name.Similar Kw 4
    ...    ${INDENT}RecLibrary1.Similar Kw 3
    ...    ${INDENT}recommendation_resource_2.Similar Kw 2
    ...    ${INDENT}recommendation_resource_1.Similar Kw 1
    Similar Kw

Non-similar Embedded User Keyword
    [Documentation]    FAIL    No keyword with name 'Unique misspelled kkw blah' found.
    Unique misspelled kkw blah

Embedded Similar User Keywords
    [Documentation]    FAIL    No keyword with name 'Embbedded User joe Argument password Keyword 3' found.
    Embbedded User joe Argument password Keyword 3

Existing Non-ASCII Keyword
    [Documentation]    FAIL
    ...    No keyword with name 'hyvää öytä' found. Did you mean:
    ...    ${INDENT}Hyvää yötä
    hyvää öytä

Wrong Library Name
    [Documentation]    FAIL    No keyword with name 'NoSuchLib.Nothing' found.
    NoSuchLib.Nothing

Wrong Library Name 2
    [Documentation]    FAIL    No keyword with name 'NoSuchLib.Action' found.
    NoSuchLib.Action

BuiltIn Similar To Other BuiltIns
    [Documentation]    FAIL
    ...    No keyword with name 'Atcion And Ignore Problems' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Action And Ignore Problems
    Atcion And Ignore Problems

Substring of Long Keyword
    [Documentation]    FAIL    No keyword with name 'Really Long Keyword' found.
    Really Long Keyword

Similar To Really Long Keyword
    [Documentation]    FAIL
    ...    No keyword with name 'Reallly Long Keyword that doesn't end for a while' found. Did you mean:
    ...    ${INDENT}Really long keyword that does not end for quite a while
    Reallly Long Keyword that doesn't end for a while

Misspelled Keyword With Arguments
    [Documentation]    FAIL
    ...    No keyword with name 'recoord' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Record
    recoord    message=hello world    level=WARN

Just Library Name
    [Documentation]    FAIL    No keyword with name 'RecLibrary1' found.
    RecLibrary1

Leading Period Keyword
    [Documentation]    FAIL    No keyword with name '.Nothing' found.
    .Nothing

Leading Period Library Name
    [Documentation]    FAIL    No keyword with name '.RecLibrary1' found.
    .RecLibrary1

Ending In Period Keyword
    [Documentation]    FAIL    No keyword with name 'Nothing.' found.
    Nothing.

Ending In Period Library Name
    [Documentation]    FAIL    No keyword with name 'RecLibrary1.' found.
    RecLibrary1.

Period
    [Documentation]    FAIL    No keyword with name '.' found.
    .

Underscore
    [Documentation]    FAIL    No keyword with name '_' found.
    _

Dollar
    [Documentation]    FAIL    No keyword with name '$' found.
    $

Curly Brace
    [Documentation]    FAIL    No keyword with name '{}' found.
    {}

More Non-ASCII
    [Documentation]    FAIL    No keyword with name 'ლ(ಠ益ಠლ)' found.
    ლ(ಠ益ಠლ)

Non-ASCII But Similar
    [Documentation]    FAIL
    ...    No keyword with name 'Similär Kw' found. Did you mean:
    ...    ${INDENT}Similar Kw 5
    ...    ${INDENT}Rec Library 2 With Custom Name.Similar Kw 4
    ...    ${INDENT}RecLibrary1.Similar Kw 3
    ...    ${INDENT}recommendation_resource_2.Similar Kw 2
    ...    ${INDENT}recommendation_resource_1.Similar Kw 1
    Similär Kw

Explicit Many Similar Keywords
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary1.Edit Data' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Get Data
    ...    ${INDENT}RecLibrary1.Read Data
    ...    ${INDENT}RecLibrary1.Update Data
    ...    ${INDENT}RecLibrary1.Modify Data
    ...    ${INDENT}RecLibrary1.Delete Data
    ...    ${INDENT}RecLibrary1.Create Data
    RecLibrary1.Edit Data

Implicit Many Similar Keywords
    [Documentation]    FAIL
    ...    No keyword with name 'Edit Data' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Get Data
    ...    ${INDENT}RecLibrary1.Read Data
    Edit Data

Explicit Substring Of Many Keywords
    [Documentation]    FAIL
    ...    No keyword with name 'RecLibrary1.Data' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Get Data
    ...    ${INDENT}RecLibrary1.Read Data
    RecLibrary1.Data

Implicit Substring Of Many Keywords
    [Documentation]    FAIL
    ...    No keyword with name 'Data' found. Did you mean:
    ...    ${INDENT}RecLibrary1.Get Data
    ...    ${INDENT}RecLibrary1.Read Data
    Data

Missing separator between keyword and arguments
    [Documentation]    FAIL
    ...    No keyword with name 'Should Be Equal ${variable} 42' found. \
    ...    Did you try using keyword 'BuiltIn.Should Be Equal' and \
    ...    forgot to use enough whitespace between keyword and arguments?
    Should Be Equal ${variable} 42

Missing separator between keyword and arguments with multiple matches
    [Documentation]    FAIL
    ...    No keyword with name 'Should Be Equal As Integers ${variable} 42' found. \
    ...    Did you try using keyword 'BuiltIn.Should Be Equal' or \
    ...    'BuiltIn.Should Be Equal As Integers' and \
    ...    forgot to use enough whitespace between keyword and arguments?
    Should Be Equal As Integers ${variable} 42

*** Keywords ***
A User Keyword
    No Operation

Similar User Keyword 1
    No Operation

Similar User Keyword 2
    No Operation

Similar User Keyword 3
    No Operation

Embedded User ${hello} Argument ${world} Keyword 1
    No Operation

Embedded User ${foo} Argument ${bar} Keyword 2
    No Operation
Hyvää yötä

Unique ${i} Kw ${j}
    No Operation

Key.word.with periods.
    No Operation

Hyvää yötä
    No Operation

Really long keyword that does not end for quite a while
    No Operation

Similar Kw 5
    No Operation
