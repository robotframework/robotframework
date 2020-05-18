*** Test cases ***
Test Flattened keyword
    Flattened keyword

Test removed keyword
    Higher keyword

Test reduced keyword
    Reduced keyword

Protection against premature flattening
    [Documentation]    A msg tag is not accepted by rebot directly under a test node
                ...    so this is prevented by specific protection code
    Removed keyword

Keyword with tag args
    This has tag args    [Pretend tag]

2 layers
    -    Run keyword    Log     Hello
    Several keywords

*** Keywords ***
Several keywords
    Log    Hello
    -    Log    There
    Set log level    robot:reduce
    Log    How are you
    -    Log    doing

-
    [Tags]    robot:flatten-2
    [Arguments]    @{kw}
    Run keyword    @{kw}

Flattened keyword
    [Tags]    robot:flatten
    Log    This text should show under Log within the test, Flattened keyword should not be visible

Higher keyword
    Removed keyword
    Log    This text should show under Log, but the removed keyword and text is nowhere to be seen

Removed keyword
    [Tags]    robot:remove
    Log    This text should show under higher keyword, not under Removed keyword or Log

Reduced keyword
    [Tags]    robot:reduce
    Log    This text should show under reduced keyword, not under Log

This has tag args
    [Arguments]    @{args}
    Log    ${args}