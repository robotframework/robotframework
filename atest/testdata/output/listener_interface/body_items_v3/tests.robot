*** Settings ***
Library           Library.py
Suite Teardown    validate_events

*** Test Cases ***
Library keyword
    Library keyword

User keyword
    User keyword

IF
    IF    False
        Library keyword
    ELSE IF    True
        User keyword
    ELSE
        Non-existing keyword
    END

TRY
    TRY
        Fail    Message
    EXCEPT    Message
        Library keyword
    ELSE
        Non-existing keyword
    FINALLY
        User keyword
    END

FOR
    FOR    ${i}    ${x}    IN ENUMERATE    a    b    c
        CONTINUE
    END

WHILE
    WHILE    True
        BREAK
    END

VAR
    VAR    ${x}    value
    VAR    ${y}    value    scope=suite
    Should Be Equal    ${x}    ${y}

Non-existing keyword
    [Documentation]    FAIL No keyword with name 'Non-existing keyword' found.
    Non-existing keyword

Empty keyword
    [Documentation]    FAIL User keyword cannot be empty.
    Empty keyword

Duplicate keyword
    [Documentation]    FAIL Keyword with same name defined multiple times.
    Duplicate keyword

Invalid keyword
    [Documentation]    FAIL Invalid argument specification: Invalid argument syntax 'bad'.
    Invalid keyword

Invalid syntax
    [Documentation]    FAIL Non-existing setting 'Bad'.
    [Bad]    setting

*** Keywords ***
User keyword
    Library keyword
    RETURN    value

Empty keyword

Duplicate keyword

Duplicate keyword

Invalid keyword
    [Arguments]    bad
