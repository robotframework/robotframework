*** Settings ***
Library    JavaListenerLibrary

*** Test Cases ***
Java suite scope library gets events
    Events should be    start suite Suite Scope Java
        ...             start test Java suite scope library gets events
        ...             start kw JavaListenerLibrary.Events Should Be

New java test gets previous suite scope events
    Events should be    start suite Suite Scope Java
            ...         start test Java suite scope library gets events
            ...         start kw JavaListenerLibrary.Events Should Be
            ...         end kw JavaListenerLibrary.Events Should Be
            ...         end test Java suite scope library gets events
            ...         start test New java test gets previous suite scope events
            ...         start kw JavaListenerLibrary.Events Should Be

Listener methods in library are keywords
    endTest   foo
    endTest   foo   zip=zap

Listener methods starting with underscore are not keywords
    [Documentation]    FAIL
    ...    No keyword with name '_endKeyword' found. Did you mean:
    ...    ${SPACE*4}BuiltIn.Run Keyword
    _endKeyword    bar
